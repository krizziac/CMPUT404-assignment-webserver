#  coding: utf-8 
import socketserver,os


#Copyright 2023 Krizzia Concepcion

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        """
        RESOURCE USED:

        Title: Python -converting sock.recv to string
        Author: (asked by:) coffeemonitor(https://stackoverflow.com/users/271619/coffeemonitor),
                (response by:) abarnert (https://stackoverflow.com/users/908494/abarnert)
        Date Published: Dec 20, 2012
        Resource: https://stackoverflow.com/questions/13979764/python-converting-sock-recv-to-string
        License: CC BY-SA 3.0
        """
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))
      
        #extract the HTTP request
        sent_data = self.data.decode("utf-8")
        data_request = sent_data.split(" ")

        http_method = data_request[0]
        url_sent= data_request[1]
        
        if http_method != "GET":
            return self.send_405()

        #if someone tries to go up the directory via relative path,  return 404
        if "../" in url_sent:
            return self.send_404()
            
        if "//" in url_sent:
            return self.send_404()
        
        #going to "read" url and determine what status to send
        self.check_valid_url(url_sent)

        
    def check_valid_url(self, url):
        '''
        Function checks if the given url is a file or directory. If it is none of them, that indicates that the
        url given is not valid. 

        file or directory -> 200, directory with no "/" -> 301, none -> 404

        RESOURCES USED:

        Title: Python - Check if a file or directory exists
        Author: GeeksForGeeks
        Date Published: August 21, 2022 (last updated)
        Link: https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists/

        Reason: I used this site to figure out how I can check if a given url
        is a file or directory (so I can determine whether or not to give that url 
        a HTTP 200 response or HTTP 301 response).
        '''

        #check if it starts with "www"
        if ".html" in url and ".css" in url:
            url = url.replace("index.html/","")
           
        if url == "/":
            url = "/index.html"
        
        #we need the url to start with "www/"
        if url[:4] != "/www":
            user_path = "www"+url
        else:
            user_path = url[1:] #take out the beginning "/"
       
        
        #checks if it's a directory (ex. "/deep")
        if not os.path.isfile(user_path):
            if os.path.isdir(user_path):
                if  user_path[-1] == "/": #if it ends in a "/", send to 200
                    self.send_200(url)
                else:
                    self.send_301(url)
                
        if os.path.isfile(user_path):
            self.send_200(url)
        
        #not a valid url
        #will also send a url like: "www/index.html/" to send_404()
        if not os.path.isfile(user_path) and not os.path.isdir(user_path):
           self.send_404()
        
 

    def find_mimetype(self, url):
        '''
        Function returns the mime type based on the given url. If it does not end in a specific file extension,
        it is set to html because we render the html file by default.
        '''

        if ".html" in  url:
            mimetype  = "text/html"
        elif ".css" in url:
            mimetype = "text/css"
        else:
            mimetype = "text/html" #by default, we read the html format

        return mimetype
    
    def send_200(self,path):
        '''
        Based on the path type, we have to reformat the path so regardless of the type (file or directory),
        we can read the file. Function sends a 200 Ok message.

        RESOURCE USED:

        Title: Building a basic HTTP Server from scratch in Python 
        Author: João Ventura
        Date Published: Nov 22, 2020
        Link: https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842

        Reason: mainly used it so I can figure out how to read the index.html and base.css file and send it as a response. In addition,
        I used it to figure out how to construct the HTTP response.
    
        '''
        mimetype = self.find_mimetype(path)
       
        #if the given path does not start with /www, add it to the beginning so we can read the file
        if path[:4] != "/www":
            path = "www"+path
        else:
            #if it starts with "/www/", take out the first character so it's "www/"
            path = path[1:]

        #if this is a directory (ex. "/www/deep/", append the html file)
        if os.path.isdir(path):
            path = path+"index.html"
          
        open_f = open(path,"r").read()
        
        #the response sent by the server when a request is made
        http_response = "HTTP/1.1 200 OK\r\nContent-Type: {0}\r\nContent Length: {1}\r\n\r\n ".format(mimetype,path)
        #append the file being read at the end of http response
        http_response = http_response+open_f+"\r\n"
        return self.request.sendall(bytearray(http_response,"utf-8"))
     
    def send_404(self):
        '''
        Function returns a 404 response for urls that do not exist in the directory
        '''
        return self.request.sendall(bytearray("HTTP/1.1 404 Path Not Found\r\n","utf-8"))
    
    def send_405(self):
        '''
        Function returns 405 for requests that do not include "GET"
        '''
        return self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n","utf-8"))

    def send_301(self,url):
        '''
        Redirects the url and appends a "/" at the end
        '''
        mimetype = self.find_mimetype(url)
       
       #if it does not end with a "/"
        if url[-1] != "/":
             url = url+'/'

       #Mainly to catch unexpected urls
        if url[0] != '/':
            url= '/'+url

        new_location = "http://127.0.0.1:8080"+url
        http_response = "HTTP/1.1 301 Moved Permanently\r\nContent-Type: {0}\r\nLocation: {1}\r\n".format(mimetype,new_location)
        return self.request.sendall(bytearray(http_response,"utf-8"))
        


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
    

