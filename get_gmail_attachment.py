import email
import os
import base64
from typing import List
import time
from connect_to_gmail import connect_to_gmail
import re

class GmailException(Exception):
    """gmail base exception class"""

class NoEmailFound(GmailException):
    """no email found"""

def search_emails(query_stirng: str, label_ids: List = None):
    try:
        message_list_response = service.users().messages().list(
            userId='me',
            labelIds=label_ids,
            q=query_string
        ).execute()

        message_items = message_list_response.get('messages')
        next_page_token = message_list_response.get('nextPageToken')

        while next_page_token:
            message_list_response = service.users().messages().list(
                userId='me',
                labelIds=label_ids,
                q=query_string,
                pageToken=next_page_token
            ).execute()

            message_items.extend(message_list_response.get('messages'))
            next_page_token = message_list_response.get('nextPageToken')
        return message_items
    except Exception as e:
        raise NoEmailFound('No emails returned')

def get_file_data(message_id, attachment_id, file_name, save_location):
    response = service.users().messages().attachments().get(
        userId='me',
        messageId=message_id,
        id=attachment_id
    ).execute()

    file_data = base64.urlsafe_b64decode(response.get('data').encode('UTF-8'))
    return file_data

def get_message_detail(message_id, msg_format='metadata', metadata_headers: List = None):
    message_detail = service.users().messages().get(
        userId='me',
        id=message_id,
        format=msg_format,
        metadataHeaders=metadata_headers
    ).execute()
    return message_detail

if __name__ == '__main__':
    CLIENT_FILE = 'credentials.json'
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    service = connect_to_gmail(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)

    query_string = 'has:attachment'

    # save_location = os.getcwd()
    base_location = os.path.abspath(os.path.join(os.getcwd(), "..","GMAIL API Output"))

    email_messages = search_emails(query_string, ['UNREAD', 'INBOX'])

    for email_message in email_messages:
        messageDetail = get_message_detail(email_message['id'], msg_format='full', metadata_headers=['parts'])
        messageDetailPayload = messageDetail.get('payload')

        # Get some email info
        msgId = messageDetail['id']
        msgLabels = messageDetail['labelIds']
        msgSnip = messageDetail['snippet']
        msgInternalDate = messageDetail['internalDate']

        if 'headers' in messageDetailPayload:
            for msgHeader in messageDetailPayload['headers']:
                if msgHeader['name']=="From":
                    msgSentFrom = msgHeader['value']
                if msgHeader['name']=="Date":
                    msgSentDate = msgHeader['value']
                if msgHeader['name']=="Subject":
                    try:
                        msgSubject = msgHeader['value']
                        pattern = "Fwd: New Assignment(.*)" # Strip off un-needed text
                        compiled = re.compile(pattern)
                        ms = compiled.search(msgSubject)
                        msgSubject = ms.group(1).strip() 
                    except:
                        pass

        if 'parts' in messageDetailPayload:
            for msgPayload in messageDetailPayload['parts']:
                
                file_name = msgSubject + '_' + msgPayload['filename']
                body = msgPayload['body']

                if 'attachmentId' in body:
                    attachment_id = body['attachmentId']
                    attachment_content = get_file_data(email_message['id'], attachment_id, file_name, base_location)
        
        print(f'ID: {msgId}')
        print(f'Labels: {msgLabels}')
        print(f'Snippet: {msgSnip}')
        print(f'Received by Google Date: {msgInternalDate}')
        print(f'Message Sent From:  {msgSentFrom}')
        print(f'Message Sent Date:  {msgSentDate}')
        print(f'Message Subject:  {msgSubject}')
        
        # Create folders based on assignment, messageID, and timestamp/epoch date
        save_location = os.path.join(base_location, msgSubject + '_' + msgId + '_'+  msgInternalDate)
        os.mkdir(save_location)
        
        with open(os.path.join(save_location, file_name), 'wb') as _f:
            _f.write(attachment_content)
            print(f'File {file_name} is saved at {save_location}')
            time.sleep(0.5)
