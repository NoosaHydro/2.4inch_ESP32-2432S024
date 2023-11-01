_M='Object moved temporarily -- see URI list'
_L='message'
_K='MicroWebTemplate'
_J='Connection'
_I='Unknown reason'
_H='image/jpeg'
_G='application/json'
_F='text/html'
_E='UTF-8'
_D='/'
_C=True
_B=False
_A=None
from json import loads,dumps
from os import stat
from _thread import start_new_thread
import socket,gc,re
try:from microWebTemplate import MicroWebTemplate
except:pass
try:from microWebSocket import MicroWebSocket
except:pass
class MicroWebSrvRoute:
	def __init__(self,route,method,func,routeArgNames,routeRegex):self.route=route;self.method=method;self.func=func;self.routeArgNames=routeArgNames;self.routeRegex=routeRegex
class MicroWebSrv:
	_indexPages=['index.pyhtml','index.html','index.htm','default.pyhtml','default.html','default.htm'];_mimeTypes={'.txt':'text/plain','.htm':_F,'.html':_F,'.css':'text/css','.csv':'text/csv','.js':'application/javascript','.xml':'application/xml','.xhtml':'application/xhtml+xml','.json':_G,'.zip':'application/zip','.pdf':'application/pdf','.ts':'application/typescript','.woff':'font/woff','.woff2':'font/woff2','.ttf':'font/ttf','.otf':'font/otf','.jpg':_H,'.jpeg':_H,'.png':'image/png','.gif':'image/gif','.svg':'image/svg+xml','.ico':'image/x-icon'};_encodings=('.gz','gzip'),('.br','br'),('','identity'),('','');_html_escape_chars={'&':'&amp;','"':'&quot;',"'":'&apos;','>':'&gt;','<':'&lt;'};_pyhtmlPagesExt='.pyhtml';_docoratedRouteHandlers=[]
	@classmethod
	def route(cls,url,method='GET'):
		def route_decorator(func):item=url,method,func;cls._docoratedRouteHandlers.append(item);return func
		return route_decorator
	@staticmethod
	def HTMLEscape(s):return''.join(MicroWebSrv._html_escape_chars.get(c,c)for c in s)
	@staticmethod
	def _startThread(func,args=()):
		try:start_new_thread(func,args)
		except:
			global _mwsrv_thread_id
			try:_mwsrv_thread_id+=1
			except:_mwsrv_thread_id=0
			try:start_new_thread('MWSRV_THREAD_%s'%_mwsrv_thread_id,func,args)
			except:return _B
		return _C
	@staticmethod
	def _unquote(s):
		r=str(s).split('%')
		try:
			b=r[0].encode()
			for i in range(1,len(r)):
				try:b+=bytes([int(r[i][:2],16)])+r[i][2:].encode()
				except:b+=b'%'+r[i].encode()
			return b.decode(_E)
		except:return str(s)
	@staticmethod
	def _unquote_plus(s):return MicroWebSrv._unquote(s.replace('+',' '))
	@staticmethod
	def _fileExists(path):
		try:stat(path);return _C
		except:return _B
	@staticmethod
	def _isPyHTMLFile(filename):return filename.lower().endswith(MicroWebSrv._pyhtmlPagesExt)
	def __init__(self,routeHandlers=[],port=80,bindIP='0.0.0.0',webPath='/flash/www'):
		self._srvAddr=bindIP,port;self._webPath=webPath;self._notFoundUrl=_A;self._started=_B;self.MaxWebSocketRecvLen=1024;self.WebSocketThreaded=_C;self.AcceptWebSocketCallback=_A;self.LetCacheStaticContentLevel=2;self._routeHandlers=[];routeHandlers+=self._docoratedRouteHandlers
		for(route,method,func)in routeHandlers:
			routeParts=route.split(_D);routeArgNames=[];routeRegex=''
			for s in routeParts:
				if s.startswith('<')and s.endswith('>'):routeArgNames.append(s[1:-1]);routeRegex+='/(\\w*)'
				elif s:routeRegex+=_D+s
			routeRegex+='$';routeRegex=re.compile(routeRegex);self._routeHandlers.append(MicroWebSrvRoute(route,method,func,routeArgNames,routeRegex))
	def _serverProcess(self):
		self._started=_C
		while _C:
			try:client,cliAddr=self._server.accept()
			except Exception as ex:
				if ex.args and ex.args[0]==113:break
				continue
			self._client(self,client,cliAddr)
		self._started=_B
	def Start(self,threaded=_B):
		if not self._started:
			self._server=socket.socket();self._server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);self._server.bind(self._srvAddr);self._server.listen(16)
			if threaded:MicroWebSrv._startThread(self._serverProcess)
			else:self._serverProcess()
	def Stop(self):
		if self._started:self._server.close()
	def IsStarted(self):return self._started
	def SetNotFoundPageUrl(self,url=_A):self._notFoundUrl=url
	def GetMimeTypeFromFilename(self,filename,encoding=''):
		filename=filename.lower()
		for(encoding_ext,enc)in self._encodings:
			if encoding==enc:break
		for ext in self._mimeTypes:
			if filename.endswith(ext+encoding_ext):return self._mimeTypes[ext]
	def GetEncodingFromFilename(self,filename):
		filename=filename.lower()
		for(ext,enc)in self._encodings:
			if ext and filename.endswith(ext):return enc
	def GetRouteHandler(self,resUrl,method):
		if self._routeHandlers:
			if resUrl.endswith(_D):resUrl=resUrl[:-1]
			method=method.upper()
			for rh in self._routeHandlers:
				if rh.method==method:
					m=rh.routeRegex.match(resUrl)
					if m:
						if rh.routeArgNames:
							routeArgs={}
							for(i,name)in enumerate(rh.routeArgNames):
								value=m.group(i+1)
								try:value=int(value)
								except:pass
								routeArgs[name]=value
							return rh.func,routeArgs
						else:return rh.func,_A
		return _A,_A
	def _physPathWithEncodings(self,path,encodings=[]):
		for(extension,enc)in self._encodings:
			if enc==''or enc in encodings or'*'in encodings:
				physPath=path+extension
				if MicroWebSrv._fileExists(physPath):return physPath
	def _physPathFromURLPath(self,urlPath,encodings=[]):
		if urlPath==_D:
			for idxPage in self._indexPages:
				physPath=self._physPathWithEncodings(self._webPath+_D+idxPage,encodings)
				if physPath:return physPath
		else:return self._physPathWithEncodings(self._webPath+urlPath.replace('../',_D),encodings)
	class _client:
		def __init__(self,microWebSrv,socket,addr):
			socket.settimeout(2);self._microWebSrv=microWebSrv;self._socket=socket;self._addr=addr;self._method=_A;self._path=_A;self._httpVer=_A;self._resPath=_D;self._queryString='';self._queryParams={};self._headers={};self._contentType=_A;self._contentLength=0
			if hasattr(socket,'readline'):self._socketfile=self._socket
			else:self._socketfile=self._socket.makefile('rwb')
			self._processRequest()
		def _processRequest(self):
			try:
				response=MicroWebSrv._response(self)
				if self._parseFirstLine(response):
					if self._parseHeader(response):
						upg=self._getConnUpgrade()
						if not upg:
							routeHandler,routeArgs=self._microWebSrv.GetRouteHandler(self._resPath,self._method)
							if routeHandler:
								try:
									if routeArgs is not _A:routeHandler(self,response,routeArgs)
									else:routeHandler(self,response)
								except Exception as ex:print('MicroWebSrv handler exception:\r\n  - In route %s %s\r\n  - %s'%(self._method,self._resPath,ex));raise ex
							elif self._method.upper()=='GET':
								encodings=[enc.strip().split(';')[0]for enc in self._headers.get('accept-encoding','').split(',')];filepath=self._microWebSrv._physPathFromURLPath(self._resPath,encodings)
								if filepath:
									if MicroWebSrv._isPyHTMLFile(filepath):response.WriteResponsePyHTMLFile(filepath)
									else:
										encoding=self._microWebSrv.GetEncodingFromFilename(filepath);contentType=self._microWebSrv.GetMimeTypeFromFilename(filepath,encoding)
										if contentType:
											headers={}
											if encoding:headers['Content-Encoding']=encoding
											if self._microWebSrv.LetCacheStaticContentLevel>0:
												if self._microWebSrv.LetCacheStaticContentLevel>1 and'if-modified-since'in self._headers:response.WriteResponseNotModified()
												else:headers['Last-Modified']='Fri, 1 Jan 2018 23:42:00 GMT';headers['Cache-Control']='max-age=315360000';response.WriteResponseFile(filepath,contentType,headers)
											else:response.WriteResponseFile(filepath,contentType)
										else:response.WriteResponseForbidden()
								else:response.WriteResponseNotFound()
							else:response.WriteResponseMethodNotAllowed()
						elif upg=='websocket'and'MicroWebSocket'in globals()and self._microWebSrv.AcceptWebSocketCallback:MicroWebSocket(socket=self._socket,httpClient=self,httpResponse=response,maxRecvLen=self._microWebSrv.MaxWebSocketRecvLen,threaded=self._microWebSrv.WebSocketThreaded,acceptCallback=self._microWebSrv.AcceptWebSocketCallback);return
						else:response.WriteResponseNotImplemented()
					else:response.WriteResponseBadRequest()
			except:response.WriteResponseInternalServerError()
			try:
				if self._socketfile is not self._socket:self._socketfile.close()
				self._socket.close()
			except:pass
		def _parseFirstLine(self,response):
			try:
				elements=self._socketfile.readline().decode().strip().split()
				if len(elements)==3:
					self._method=elements[0].upper();self._path=elements[1];self._httpVer=elements[2].upper();elements=self._path.split('?',1)
					if len(elements)>0:
						self._resPath=MicroWebSrv._unquote_plus(elements[0])
						if len(elements)>1:
							self._queryString=MicroWebSrv._unquote_plus(elements[1]);elements=self._queryString.split('&')
							for s in elements:
								param=s.split('=',1)
								if len(param)>0:value=MicroWebSrv._unquote(param[1])if len(param)>1 else'';self._queryParams[MicroWebSrv._unquote(param[0])]=value
					return _C
			except:pass
			return _B
		def _parseHeader(self,response):
			while _C:
				elements=self._socketfile.readline().decode().strip().split(':',1)
				if len(elements)==2:self._headers[elements[0].strip().lower()]=elements[1].strip()
				elif len(elements)==1 and len(elements[0])==0:
					if self._method=='POST'or self._method=='PUT':self._contentType=self._headers.get('content-type',_A);self._contentLength=int(self._headers.get('content-length',0))
					return _C
				else:return _B
		def _getConnUpgrade(self):
			A='upgrade'
			if A in self._headers.get('connection','').lower():return self._headers.get(A,'').lower()
		def GetServer(self):return self._microWebSrv
		def GetAddr(self):return self._addr
		def GetIPAddr(self):return self._addr[0]
		def GetPort(self):return self._addr[1]
		def GetRequestMethod(self):return self._method
		def GetRequestTotalPath(self):return self._path
		def GetRequestPath(self):return self._resPath
		def GetRequestQueryString(self):return self._queryString
		def GetRequestQueryParams(self):return self._queryParams
		def GetRequestHeaders(self):return self._headers
		def GetRequestContentType(self):return self._contentType
		def GetRequestContentLength(self):return self._contentLength
		def ReadRequestContent(self,size=_A):
			if size is _A:size=self._contentLength
			if size>0:
				try:return self._socketfile.read(size)
				except:pass
			return b''
		def ReadRequestPostedFormData(self):
			res={};data=self.ReadRequestContent()
			if data:
				elements=data.decode().split('&')
				for s in elements:
					param=s.split('=',1)
					if len(param)>0:value=MicroWebSrv._unquote_plus(param[1])if len(param)>1 else'';res[MicroWebSrv._unquote_plus(param[0])]=value
			return res
		def ReadRequestContentAsJSON(self):
			data=self.ReadRequestContent()
			if data:
				try:return loads(data.decode())
				except:pass
	class _response:
		def __init__(self,client):self._client=client
		def _write(self,data,strEncoding='ISO-8859-1'):
			if data:
				if type(data)==str:data=data.encode(strEncoding)
				data=memoryview(data)
				while data:
					n=self._client._socketfile.write(data)
					if n is _A:return _B
					data=data[n:]
				return _C
			return _B
		def _writeFirstLine(self,code):reason=self._responseCodes.get(code,(_I,))[0];return self._write('HTTP/1.1 %s %s\r\n'%(code,reason))
		def _writeHeader(self,name,value):return self._write('%s: %s\r\n'%(name,value))
		def _writeContentTypeHeader(self,contentType,charset=_A):
			if contentType:ct=contentType+('; charset=%s'%charset if charset else'')
			else:ct='application/octet-stream'
			self._writeHeader('Content-Type',ct)
		def _writeServerHeader(self):self._writeHeader('Server','MicroWebSrv')
		def _writeEndHeader(self):return self._write('\r\n')
		def _writeBeforeContent(self,code,headers,contentType,contentCharset,contentLength):
			self._writeFirstLine(code)
			if isinstance(headers,dict):
				for header in headers:self._writeHeader(header,headers[header])
			if contentLength>0:self._writeContentTypeHeader(contentType,contentCharset);self._writeHeader('Content-Length',contentLength)
			self._writeServerHeader();self._writeHeader(_J,'close');self._writeEndHeader()
		def WriteSwitchProto(self,upgrade,headers=_A):
			A='Upgrade';self._writeFirstLine(101);self._writeHeader(_J,A);self._writeHeader(A,upgrade)
			if isinstance(headers,dict):
				for header in headers:self._writeHeader(header,headers[header])
			self._writeServerHeader();self._writeEndHeader()
			if self._client._socketfile is not self._client._socket:self._client._socketfile.flush()
		def WriteResponse(self,code,headers,contentType,contentCharset,content):
			try:
				if content:
					if type(content)==str:content=content.encode(contentCharset)
					contentLength=len(content)
				else:contentLength=0
				self._writeBeforeContent(code,headers,contentType,contentCharset,contentLength)
				if content:return self._write(content)
				return _C
			except:return _B
		def WriteResponsePyHTMLFile(self,filepath,headers=_A,vars=_A):
			if _K in globals():
				with open(filepath,'r')as file:code=file.read()
				mWebTmpl=MicroWebTemplate(code,escapeStrFunc=MicroWebSrv.HTMLEscape,filepath=filepath)
				try:tmplResult=mWebTmpl.Execute(_A,vars);return self.WriteResponse(200,headers,_F,_E,tmplResult)
				except Exception as ex:return self.WriteResponse(500,_A,_F,_E,self._execErrCtnTmpl%{'module':'PyHTML',_L:str(ex)})
			return self.WriteResponseNotImplemented()
		def WriteResponseFile(self,filepath,contentType=_A,headers=_A):
			try:
				size=stat(filepath)[6]
				if size>0:
					with open(filepath,'rb')as file:
						self._writeBeforeContent(200,headers,contentType,_A,size)
						try:
							buf=bytearray(1024)
							while size>0:
								x=file.readinto(buf)
								if x<len(buf):buf=memoryview(buf)[:x]
								if not self._write(buf):return _B
								size-=x
							return _C
						except:self.WriteResponseInternalServerError();return _B
			except:pass
			self.WriteResponseNotFound();return _B
		def WriteResponseFileAttachment(self,filepath,attachmentName,headers=_A):
			if not isinstance(headers,dict):headers={}
			headers['Content-Disposition']='attachment; filename="%s"'%attachmentName;return self.WriteResponseFile(filepath,_A,headers)
		def WriteResponseOk(self,headers=_A,contentType=_A,contentCharset=_A,content=_A):return self.WriteResponse(200,headers,contentType,contentCharset,content)
		def WriteResponseJSONOk(self,obj=_A,headers=_A):return self.WriteResponse(200,headers,_G,_E,dumps(obj))
		def WriteResponseRedirect(self,location):headers={'Location':location};return self.WriteResponse(302,headers,_A,_A,_A)
		def WriteResponseError(self,code):responseCode=self._responseCodes.get(code,(_I,''));return self.WriteResponse(code,_A,_F,_E,self._errCtnTmpl%{'code':code,'reason':responseCode[0],_L:responseCode[1]})
		def WriteResponseJSONError(self,code,obj=_A):return self.WriteResponse(code,_A,_G,_E,dumps(obj if obj else{}))
		def WriteResponseNotModified(self):return self.WriteResponseError(304)
		def WriteResponseBadRequest(self):return self.WriteResponseError(400)
		def WriteResponseForbidden(self):return self.WriteResponseError(403)
		def WriteResponseNotFound(self):
			if self._client._microWebSrv._notFoundUrl:self.WriteResponseRedirect(self._client._microWebSrv._notFoundUrl)
			else:return self.WriteResponseError(404)
		def WriteResponseMethodNotAllowed(self):return self.WriteResponseError(405)
		def WriteResponseInternalServerError(self):return self.WriteResponseError(500)
		def WriteResponseNotImplemented(self):return self.WriteResponseError(501)
		def FlashMessage(self,messageText,messageStyle=''):
			if _K in globals():MicroWebTemplate.MESSAGE_TEXT=messageText;MicroWebTemplate.MESSAGE_STYLE=messageStyle
		_errCtnTmpl='        <html>\n            <head>\n                <title>Error</title>\n            </head>\n            <body>\n                <h1>%(code)d %(reason)s</h1>\n                %(message)s\n            </body>\n        </html>\n        ';_execErrCtnTmpl='        <html>\n            <head>\n                <title>Page execution error</title>\n            </head>\n            <body>\n                <h1>%(module)s page execution error</h1>\n                %(message)s\n            </body>\n        </html>\n        ';_responseCodes={100:('Continue','Request received, please continue'),101:('Switching Protocols','Switching to new protocol; obey Upgrade header'),200:('OK','Request fulfilled, document follows'),201:('Created','Document created, URL follows'),202:('Accepted','Request accepted, processing continues off-line'),203:('Non-Authoritative Information','Request fulfilled from cache'),204:('No Content','Request fulfilled, nothing follows'),205:('Reset Content','Clear input form for further input.'),206:('Partial Content','Partial content follows.'),300:('Multiple Choices','Object has several resources -- see URI list'),301:('Moved Permanently','Object moved permanently -- see URI list'),302:('Found',_M),303:('See Other','Object moved -- see Method and URL list'),304:('Not Modified','Document has not changed since given time'),305:('Use Proxy','You must use proxy specified in Location to access this resource.'),307:('Temporary Redirect',_M),400:('Bad Request','Bad request syntax or unsupported method'),401:('Unauthorized','No permission -- see authorization schemes'),402:('Payment Required','No payment -- see charging schemes'),403:('Forbidden','Request forbidden -- authorization will not help'),404:('Not Found','Nothing matches the given URI'),405:('Method Not Allowed','Specified method is invalid for this resource.'),406:('Not Acceptable','URI not available in preferred format.'),407:('Proxy Authentication Required','You must authenticate with this proxy before proceeding.'),408:('Request Timeout','Request timed out; try again later.'),409:('Conflict','Request conflict.'),410:('Gone','URI no longer exists and has been permanently removed.'),411:('Length Required','Client must specify Content-Length.'),412:('Precondition Failed','Precondition in headers is false.'),413:('Request Entity Too Large','Entity is too large.'),414:('Request-URI Too Long','URI is too long.'),415:('Unsupported Media Type','Entity body in unsupported format.'),416:('Requested Range Not Satisfiable','Cannot satisfy request range.'),417:('Expectation Failed','Expect condition could not be satisfied.'),500:('Internal Server Error','Server got itself in trouble'),501:('Not Implemented','Server does not support this operation'),502:('Bad Gateway','Invalid responses from another server/proxy.'),503:('Service Unavailable','The server cannot process the request due to a high load'),504:('Gateway Timeout','The gateway server did not receive a timely response'),505:('HTTP Version Not Supported','Cannot fulfill request.')}
		
