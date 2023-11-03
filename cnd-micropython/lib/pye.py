_H='\t'
_G='\n'
_F='\x08'
_E=' '
_D='y'
_C=False
_B=True
_A=None
import sys,gc
if sys.platform in('linux','darwin'):import os,signal,tty,termios;is_linux=_B
else:is_linux=_C
if sys.implementation.name=='micropython':is_micropython=_B;from uio import StringIO;from ure import compile as re_compile
else:is_micropython=_C;const=lambda x:x;from _io import StringIO;from re import compile as re_compile
PYE_VERSION=' V2.31 '
KEY_NONE=const(0)
KEY_UP=const(11)
KEY_DOWN=const(13)
KEY_LEFT=const(31)
KEY_RIGHT=const(30)
KEY_HOME=const(16)
KEY_END=const(3)
KEY_PGUP=const(65521)
KEY_PGDN=const(65522)
KEY_WORD_LEFT=const(65523)
KEY_WORD_RIGHT=const(65524)
KEY_SHIFT_UP=const(65525)
KEY_SHIFT_DOWN=const(65526)
KEY_QUIT=const(17)
KEY_ENTER=const(10)
KEY_BACKSPACE=const(8)
KEY_DELETE=const(127)
KEY_DEL_WORD=const(65527)
KEY_WRITE=const(19)
KEY_TAB=const(9)
KEY_BACKTAB=const(21)
KEY_FIND=const(6)
KEY_GOTO=const(7)
KEY_MOUSE=const(27)
KEY_SCRLUP=const(28)
KEY_SCRLDN=const(29)
KEY_FIND_AGAIN=const(14)
KEY_REDRAW=const(5)
KEY_UNDO=const(26)
KEY_YANK=const(24)
KEY_ZAP=const(22)
KEY_DUP=const(4)
KEY_FIRST=const(20)
KEY_LAST=const(2)
KEY_REPLC=const(18)
KEY_TOGGLE=const(1)
KEY_GET=const(15)
KEY_MARK=const(12)
KEY_NEXT=const(23)
KEY_COMMENT=const(65532)
KEY_MATCH=const(65533)
KEY_INDENT=const(65534)
KEY_UNDENT=const(65535)
class Editor:
	KEYMAP={'\x1b[A':KEY_UP,'\x1b[1;2A':KEY_SHIFT_UP,'\x1b[B':KEY_DOWN,'\x1b[1;2B':KEY_SHIFT_DOWN,'\x1b[D':KEY_LEFT,'\x1b[C':KEY_RIGHT,'\x1b[H':KEY_HOME,'\x1bOH':KEY_HOME,'\x1b[1~':KEY_HOME,'\x1b[F':KEY_END,'\x1bOF':KEY_END,'\x1b[4~':KEY_END,'\x1b[5~':KEY_PGUP,'\x1b[6~':KEY_PGDN,'\x1b[1;5D':KEY_WORD_LEFT,'\x1b[1;5C':KEY_WORD_RIGHT,'\x03':KEY_DUP,'\r':KEY_ENTER,'\x7f':KEY_BACKSPACE,'\x1b[3~':KEY_DELETE,'\x1b[Z':KEY_BACKTAB,'\x19':KEY_YANK,_F:KEY_REPLC,'\x12':KEY_REPLC,'\x11':KEY_QUIT,'\x1bq':KEY_QUIT,_G:KEY_ENTER,'\x13':KEY_WRITE,'\x06':KEY_FIND,'\x0e':KEY_FIND_AGAIN,'\x07':KEY_GOTO,'\x05':KEY_REDRAW,'\x1a':KEY_UNDO,_H:KEY_TAB,'\x15':KEY_BACKTAB,'\x18':KEY_YANK,'\x16':KEY_ZAP,'\x04':KEY_DUP,'\x0c':KEY_MARK,'\x00':KEY_MARK,'\x14':KEY_FIRST,'\x02':KEY_LAST,'\x01':KEY_TOGGLE,'\x17':KEY_NEXT,'\x0f':KEY_GET,'\x10':KEY_COMMENT,'\x1b[1;5A':KEY_SCRLUP,'\x1b[1;5B':KEY_SCRLDN,'\x1b[1;5H':KEY_FIRST,'\x1b[1;5F':KEY_LAST,'\x1b[3;5~':KEY_DEL_WORD,'\x0b':KEY_MATCH,'\x1b[M':KEY_MOUSE};yank_buffer=[];find_pattern='';case='n';autoindent=_D;replc_pattern='';comment_char='# ';word_char='_\\'
	def __init__(self,tab_size,undo_limit):self.top_line=self.cur_line=self.row=self.col=self.margin=0;self.tab_size=tab_size;self.changed='';self.message=self.fname='';self.content=[''];self.undo=[];self.undo_limit=max(undo_limit,0);self.undo_zero=0;self.mark=_A;self.write_tabs='n'
	if is_micropython and not is_linux:
		def wr(self,s):sys.stdout.write(s)
		def rd(self):return sys.stdin.read(1)
		@staticmethod
		def init_tty(device):
			try:from micropython import kbd_intr;kbd_intr(-1)
			except ImportError:pass
		@staticmethod
		def deinit_tty():
			try:from micropython import kbd_intr;kbd_intr(3)
			except ImportError:pass
	def goto(self,row,col):self.wr('\x1b[{};{}H'.format(row+1,col+1))
	def clear_to_eol(self):self.wr('\x1b[0K')
	def cursor(self,onoff):self.wr('\x1b[?25h'if onoff else'\x1b[?25l')
	def hilite(self,mode):
		if mode==1:self.wr('\x1b[1;47m')
		elif mode==2:self.wr('\x1b[43m')
		else:self.wr('\x1b[0m')
	def mouse_reporting(self,onoff):self.wr('\x1b[?9h'if onoff else'\x1b[?9l')
	def scroll_region(self,stop):self.wr('\x1b[1;{}r'.format(stop)if stop else'\x1b[r')
	def scroll_up(self,scrolling):Editor.scrbuf[scrolling:]=Editor.scrbuf[:-scrolling];Editor.scrbuf[:scrolling]=['']*scrolling;self.goto(0,0);self.wr('\x1bM'*scrolling)
	def scroll_down(self,scrolling):Editor.scrbuf[:-scrolling]=Editor.scrbuf[scrolling:];Editor.scrbuf[-scrolling:]=['']*scrolling;self.goto(Editor.height-1,0);self.wr(_G*scrolling)
	def get_screen_size(self):
		self.wr('\x1b[999;999H\x1b[6n');pos='';char=self.rd()
		while char!='R':pos+=char;char=self.rd()
		return[int(i,10)for i in pos.lstrip('\n\x1b[').split(';')]
	def redraw(self,flag):
		self.cursor(_C);Editor.height,Editor.width=self.get_screen_size();Editor.height-=1;Editor.scrbuf=[(_C,'\x00')]*Editor.height;self.row=min(Editor.height-1,self.row);self.scroll_region(Editor.height);self.mouse_reporting(_B)
		if flag:self.message=PYE_VERSION
		if is_linux and not is_micropython:signal.signal(signal.SIGWINCH,Editor.signal_handler)
		if is_micropython:
			gc.collect()
			if flag:self.message+='{} Bytes Memory available'.format(gc.mem_free())
	def get_input(self):
		while _B:
			in_buffer=self.rd()
			if in_buffer=='\x1b':
				while _B:
					in_buffer+=self.rd();c=in_buffer[-1]
					if c=='~'or c.isalpha()and c!='O':break
			if in_buffer in self.KEYMAP:
				c=self.KEYMAP[in_buffer]
				if c!=KEY_MOUSE:return c,_A
				else:
					mouse_fct=ord(self.rd());mouse_x=ord(self.rd())-33;mouse_y=ord(self.rd())-33
					if mouse_fct==97:return KEY_SCRLDN,_A
					elif mouse_fct==96:return KEY_SCRLUP,_A
					else:return KEY_MOUSE,[mouse_x,mouse_y,mouse_fct]
			elif ord(in_buffer[0])>=32:return KEY_NONE,in_buffer
	def display_window(self):
		self.cur_line=min(self.total_lines-1,max(self.cur_line,0));self.col=max(0,min(self.col,len(self.content[self.cur_line])))
		if self.col>=Editor.width+self.margin:self.margin=self.col-Editor.width+(Editor.width>>2)
		elif self.col<self.margin:self.margin=max(self.col-(Editor.width>>2),0)
		if not self.top_line<=self.cur_line<self.top_line+Editor.height:self.top_line=max(self.cur_line-self.row,0)
		self.row=self.cur_line-self.top_line;self.cursor(_C);i=self.top_line;low_mark,high_mark=(-2,-1)if self.mark is _A else self.line_range()
		for c in range(Editor.height):
			if i==self.total_lines:
				if Editor.scrbuf[c]!=(_C,''):self.goto(c,0);self.clear_to_eol();Editor.scrbuf[c]=_C,''
			else:
				l=low_mark<=i<high_mark,self.content[i][self.margin:self.margin+Editor.width]
				if l!=Editor.scrbuf[c]:
					self.goto(c,0)
					if l[0]:self.hilite(2)
					self.wr(l[1])
					if len(l[1])<Editor.width:self.clear_to_eol()
					if l[0]:self.hilite(0)
					Editor.scrbuf[c]=l
				i+=1
		self.goto(Editor.height,0);self.hilite(1);self.wr('{}{} Row: {}/{} Col: {}  {}'.format(self.changed,self.fname,self.cur_line+1,self.total_lines,self.col+1,self.message)[:self.width-1]);self.clear_to_eol();self.hilite(0);self.goto(self.row,self.col-self.margin);self.cursor(_B)
	def spaces(self,line,pos=_A):return len(line)-len(line.lstrip(_E))if pos is _A else len(line[:pos])-len(line[:pos].rstrip(_E))
	def line_range(self):return(self.mark,self.cur_line+1)if self.mark<self.cur_line else(self.cur_line,self.mark+1)
	def line_edit(self,prompt,default,zap=_A):
		push_msg=lambda msg:self.wr(msg+_F*len(msg));self.goto(Editor.height,0);self.hilite(1);self.wr(prompt);self.wr(default);self.clear_to_eol();res=default;pos=len(res)
		while _B:
			key,char=self.get_input()
			if key==KEY_NONE:
				if len(prompt)+len(res)<self.width-2:res=res[:pos]+char+res[pos:];self.wr(res[pos]);pos+=len(char);push_msg(res[pos:])
			elif key in(KEY_ENTER,KEY_TAB):self.hilite(0);return res
			elif key in(KEY_QUIT,KEY_DUP):self.hilite(0);return
			elif key==KEY_LEFT:
				if pos>0:self.wr(_F);pos-=1
			elif key==KEY_RIGHT:
				if pos<len(res):self.wr(res[pos]);pos+=1
			elif key==KEY_HOME:self.wr(_F*pos);pos=0
			elif key==KEY_END:self.wr(res[pos:]);pos=len(res)
			elif key==KEY_DELETE:
				if pos<len(res):res=res[:pos]+res[pos+1:];push_msg(res[pos:]+_E)
			elif key==KEY_BACKSPACE:
				if pos>0:res=res[:pos-1]+res[pos:];self.wr(_F);pos-=1;push_msg(res[pos:]+_E)
			elif key==KEY_ZAP:
				char=self.getsymbol(self.content[self.cur_line],self.col,zap)
				if char is not _A:self.wr(_F*pos+_E*len(res)+_F*len(res));res=char;self.wr(res);pos=len(res)
	def getsymbol(self,s,pos,zap):
		if pos<len(s)and zap is not _A:start=self.skip_while(s,pos,zap,-1);stop=self.skip_while(s,pos,zap,1);return s[start+1:stop]
	def issymbol(self,c,zap):return c.isalpha()or c.isdigit()or c in zap
	def skip_until(self,s,pos,zap,way):
		stop=-1 if way<0 else len(s)
		while pos!=stop and not self.issymbol(s[pos],zap):pos+=way
		return pos
	def skip_while(self,s,pos,zap,way):
		stop=-1 if way<0 else len(s)
		while pos!=stop and self.issymbol(s[pos],zap):pos+=way
		return pos
	def move_up(self):
		if self.cur_line>0:
			self.cur_line-=1
			if self.cur_line<self.top_line:self.scroll_up(1)
	def skip_up(self):
		if self.col==0 and self.cur_line>0:self.col=len(self.content[self.cur_line-1]);self.move_up();return _B
		else:return _C
	def move_down(self):
		if self.cur_line<self.total_lines-1:
			self.cur_line+=1
			if self.cur_line==self.top_line+Editor.height:self.scroll_down(1)
	def skip_down(self,l):
		if self.col>=len(l)and self.cur_line<self.total_lines-1:self.col=0;self.move_down();return _B
		else:return _C
	def find_in_file(self,pattern,col,end):
		Editor.find_pattern=pattern
		if Editor.case!=_D:pattern=pattern.lower()
		try:rex=re_compile(pattern)
		except:self.message='Invalid pattern: '+pattern;return
		start=self.cur_line
		if col>len(self.content[start])or pattern[0]=='^'and col!=0:start,col=start+1,0
		for line in range(start,end):
			l=self.content[line][col:]
			if Editor.case!=_D:l=l.lower()
			match=rex.search(l)
			if match:
				self.cur_line=line
				if pattern[-1:]=='$'and match.group(0)[-1:]!='$':self.col=col+len(l)-len(match.group(0))
				else:self.col=col+l.find(match.group(0))
				return len(match.group(0))
			col=0
		else:self.message=pattern+' not found (again)';return
	def undo_add(self,lnum,text,key,span=1):
		self.changed='*'
		if self.undo_limit>0 and(len(self.undo)==0 or key==KEY_NONE or self.undo[-1][3]!=key or self.undo[-1][0]!=lnum):
			if len(self.undo)>=self.undo_limit:del self.undo[0];self.undo_zero-=1
			self.undo.append([lnum,span,text,key,self.col])
	def delete_lines(self,yank):
		lrange=self.line_range()
		if yank:Editor.yank_buffer=self.content[lrange[0]:lrange[1]]
		self.undo_add(lrange[0],self.content[lrange[0]:lrange[1]],KEY_NONE,0);del self.content[lrange[0]:lrange[1]]
		if self.content==[]:self.content=[''];self.undo[-1][1]=1
		self.total_lines=len(self.content);self.cur_line=lrange[0];self.mark=_A
	def handle_edit_keys(self,key,char):
		A='_';l=self.content[self.cur_line]
		if key==KEY_NONE:self.mark=_A;self.undo_add(self.cur_line,[l],32 if char==_E else 65);self.content[self.cur_line]=l[:self.col]+char+l[self.col:];self.col+=len(char)
		elif key==KEY_DOWN:self.move_down()
		elif key==KEY_UP:self.move_up()
		elif key==KEY_LEFT:
			if not self.skip_up():self.col-=1
		elif key==KEY_RIGHT:
			if not self.skip_down(l):self.col+=1
		elif key==KEY_WORD_LEFT:
			if self.skip_up():l=self.content[self.cur_line]
			pos=self.skip_until(l,self.col-1,self.word_char,-1);self.col=self.skip_while(l,pos,self.word_char,-1)+1
		elif key==KEY_WORD_RIGHT:
			if self.skip_down(l):l=self.content[self.cur_line]
			pos=self.skip_until(l,self.col,self.word_char,1);self.col=self.skip_while(l,pos,self.word_char,1)
		elif key==KEY_DELETE:
			if self.mark is not _A:self.delete_lines(_C)
			elif self.col<len(l):self.undo_add(self.cur_line,[l],KEY_DELETE);self.content[self.cur_line]=l[:self.col]+l[self.col+1:]
			elif self.cur_line+1<self.total_lines:self.undo_add(self.cur_line,[l,self.content[self.cur_line+1]],KEY_NONE);self.content[self.cur_line]=l+(self.content.pop(self.cur_line+1).lstrip()if Editor.autoindent==_D and self.col>0 else self.content.pop(self.cur_line+1));self.total_lines-=1
		elif key==KEY_BACKSPACE:
			if self.mark is not _A:self.delete_lines(_C)
			elif self.col>0:self.undo_add(self.cur_line,[l],KEY_BACKSPACE);self.content[self.cur_line]=l[:self.col-1]+l[self.col:];self.col-=1
			elif self.cur_line>0:self.undo_add(self.cur_line-1,[self.content[self.cur_line-1],l],KEY_NONE);self.col=len(self.content[self.cur_line-1]);self.content[self.cur_line-1]+=self.content.pop(self.cur_line);self.cur_line-=1;self.total_lines-=1
		elif key==KEY_DEL_WORD:
			if self.col<len(l):
				pos=self.skip_while(l,self.col,self.word_char,1);pos+=self.spaces(l[pos:])
				if self.col<pos:self.undo_add(self.cur_line,[l],KEY_DEL_WORD);self.content[self.cur_line]=l[:self.col]+l[pos:]
		elif key==KEY_HOME:self.col=self.spaces(l)if self.col==0 else 0
		elif key==KEY_END:ni=len(l.split(Editor.comment_char.strip())[0].rstrip());ns=self.spaces(l);self.col=ni if self.col>=len(l)and ni>ns else len(l)
		elif key==KEY_PGUP:self.cur_line-=Editor.height
		elif key==KEY_PGDN:self.cur_line+=Editor.height
		elif key==KEY_FIND:
			pat=self.line_edit('Find: ',Editor.find_pattern,A)
			if pat:self.find_in_file(pat,self.col,self.total_lines);self.row=Editor.height>>1
		elif key==KEY_FIND_AGAIN:
			if Editor.find_pattern:self.find_in_file(Editor.find_pattern,self.col+1,self.total_lines);self.row=Editor.height>>1
		elif key==KEY_GOTO:
			line=self.line_edit('Goto Line: ','')
			if line:self.cur_line=int(line)-1;self.row=Editor.height>>1
		elif key==KEY_FIRST:self.cur_line=0
		elif key==KEY_LAST:self.cur_line=self.total_lines-1;self.row=Editor.height-1
		elif key==KEY_TOGGLE:
			pat=self.line_edit('Autoindent {}, Search Case {}, Tabsize {}, Comment {}, Tabwrite {}: '.format(Editor.autoindent,Editor.case,self.tab_size,Editor.comment_char,self.write_tabs),'')
			try:
				res=[i.lstrip().lower()for i in pat.split(',')]
				if res[0]:Editor.autoindent=_D if res[0][0]==_D else'n'
				if res[1]:Editor.case=_D if res[1][0]==_D else'n'
				if res[2]:self.tab_size=int(res[2])
				if res[3]:Editor.comment_char=res[3]
				if res[4]:self.write_tabs=_D if res[4][0]==_D else'n'
			except:pass
		elif key==KEY_MOUSE:
			if char[1]<Editor.height:
				self.col=char[0]+self.margin;self.cur_line=char[1]+self.top_line
				if char[2]in(34,48):self.mark=self.cur_line if self.mark is _A else _A
		elif key==KEY_SCRLUP:
			if self.top_line>0:self.top_line=max(self.top_line-3,0);self.cur_line=min(self.cur_line,self.top_line+Editor.height-1);self.scroll_up(3)
		elif key==KEY_SCRLDN:
			if self.top_line+Editor.height<self.total_lines:self.top_line=min(self.top_line+3,self.total_lines-1);self.cur_line=max(self.cur_line,self.top_line);self.scroll_down(3)
		elif key==KEY_MATCH:
			if self.col<len(l):
				brackets='<{[()]}>';srch=l[self.col];i=brackets.find(srch)
				if i>=0:
					match=brackets[7-i];level=0;way=1 if i<4 else-1;i=self.cur_line;c=self.col+way;lstop=self.total_lines if way>0 else-1
					while i!=lstop:
						cstop=len(self.content[i])if way>0 else-1
						while c!=cstop:
							if self.content[i][c]==match:
								if level==0:self.cur_line,self.col=i,c;return _B
								else:level-=1
							elif self.content[i][c]==srch:level+=1
							c+=way
						i+=way;c=0 if way>0 else len(self.content[i])-1
					self.message='No match'
		elif key==KEY_MARK:self.mark=self.cur_line if self.mark is _A else _A
		elif key==KEY_SHIFT_DOWN:
			if self.mark is _A:self.mark=self.cur_line
			else:self.move_down()
		elif key==KEY_SHIFT_UP:
			if self.mark is _A:self.mark=self.cur_line
			else:self.move_up()
		elif key==KEY_ENTER:
			self.mark=_A;self.undo_add(self.cur_line,[l],KEY_NONE,2);self.content[self.cur_line]=l[:self.col];ni=0
			if Editor.autoindent==_D:ni=min(self.spaces(l),self.col)
			self.cur_line+=1;self.content[self.cur_line:self.cur_line]=[_E*ni+l[self.col:]];self.total_lines+=1;self.col=ni
		elif key==KEY_TAB:
			if self.mark is _A:self.undo_add(self.cur_line,[l],KEY_TAB);ni=self.tab_size-self.col%self.tab_size;self.content[self.cur_line]=l[:self.col]+_E*ni+l[self.col:];self.col+=ni
			else:
				lrange=self.line_range();self.undo_add(lrange[0],self.content[lrange[0]:lrange[1]],KEY_INDENT,lrange[1]-lrange[0])
				for i in range(lrange[0],lrange[1]):
					if len(self.content[i])>0:self.content[i]=_E*(self.tab_size-self.spaces(self.content[i])%self.tab_size)+self.content[i]
		elif key==KEY_BACKTAB:
			if self.mark is _A:
				ni=min((self.col-1)%self.tab_size+1,self.spaces(l,self.col))
				if ni>0:self.undo_add(self.cur_line,[l],KEY_BACKTAB);self.content[self.cur_line]=l[:self.col-ni]+l[self.col:];self.col-=ni
			else:
				lrange=self.line_range();self.undo_add(lrange[0],self.content[lrange[0]:lrange[1]],KEY_UNDENT,lrange[1]-lrange[0])
				for i in range(lrange[0],lrange[1]):
					ns=self.spaces(self.content[i])
					if ns>0:self.content[i]=self.content[i][(ns-1)%self.tab_size+1:]
		elif key==KEY_REPLC:
			count=0;pat=self.line_edit('Replace: ',Editor.find_pattern,A)
			if pat:
				rpat=self.line_edit('With: ',Editor.replc_pattern,A)
				if rpat is not _A:
					Editor.replc_pattern=rpat;q='';cur_line,cur_col=self.cur_line,self.col
					if self.mark is not _A:self.cur_line,end_line=self.line_range();self.col=0
					else:end_line=self.total_lines
					self.message='Replace (yes/No/all/quit) ? '
					while _B:
						ni=self.find_in_file(pat,self.col,end_line)
						if ni is not _A:
							if q!='a':self.display_window();key,char=self.get_input();q=char.lower()
							if q=='q'or key==KEY_QUIT:break
							elif q in('a',_D):self.undo_add(self.cur_line,[self.content[self.cur_line]],KEY_NONE);self.content[self.cur_line]=self.content[self.cur_line][:self.col]+rpat+self.content[self.cur_line][self.col+ni:];self.col+=len(rpat)+(ni==0);count+=1
							else:self.col+=1
						else:break
					self.cur_line,self.col=cur_line,cur_col;self.message="'{}' replaced {} times".format(pat,count)
		elif key==KEY_YANK:
			if self.mark is not _A:self.delete_lines(_B)
		elif key==KEY_DUP:
			if self.mark is not _A:lrange=self.line_range();Editor.yank_buffer=self.content[lrange[0]:lrange[1]];self.mark=_A
		elif key==KEY_ZAP:
			if Editor.yank_buffer:
				if self.mark is not _A:self.delete_lines(_C)
				self.undo_add(self.cur_line,_A,KEY_NONE,-len(Editor.yank_buffer));self.content[self.cur_line:self.cur_line]=Editor.yank_buffer;self.total_lines+=len(Editor.yank_buffer)
		elif key==KEY_WRITE:
			fname=self.line_edit('Save File: ',self.fname)
			if fname:self.put_file(fname);self.changed='';self.undo_zero=len(self.undo);self.fname=fname
		elif key==KEY_UNDO:
			if len(self.undo)>0:
				action=self.undo.pop(-1)
				if not action[3]in(KEY_INDENT,KEY_UNDENT,KEY_COMMENT):self.cur_line=action[0]
				self.col=action[4]
				if action[1]>=0:
					if action[0]<self.total_lines:self.content[action[0]:action[0]+action[1]]=action[2]
					else:self.content+=action[2]
				else:del self.content[action[0]:action[0]-action[1]]
				self.total_lines=len(self.content)
				if len(self.undo)==self.undo_zero:self.changed=''
				self.mark=_A
		elif key==KEY_COMMENT:
			if self.mark is _A:lrange=self.cur_line,self.cur_line+1
			else:lrange=self.line_range()
			self.undo_add(lrange[0],self.content[lrange[0]:lrange[1]],KEY_COMMENT,lrange[1]-lrange[0]);ni=len(Editor.comment_char)
			for i in range(lrange[0],lrange[1]):
				ns=self.spaces(self.content[i])
				if self.content[i][ns:ns+ni]==Editor.comment_char:self.content[i]=ns*_E+self.content[i][ns+ni:]
				else:self.content[i]=ns*_E+Editor.comment_char+self.content[i][ns:]
		elif key==KEY_REDRAW:self.redraw(_B)
	def edit_loop(self):
		if not self.content:self.content=['']
		self.total_lines=len(self.content);self.redraw(self.message=='')
		while _B:
			self.display_window();key,char=self.get_input();self.message=''
			if key==KEY_QUIT:
				if self.changed:
					res=self.line_edit('Content changed! Quit without saving (y/N)? ','N')
					if not res or res[0].upper()!='Y':continue
				self.scroll_region(0);self.mouse_reporting(_C);self.goto(Editor.height,0);self.clear_to_eol();self.undo=[];return key
			elif key in(KEY_NEXT,KEY_GET):return key
			else:self.handle_edit_keys(key,char)
	def packtabs(self,s):
		sb=StringIO()
		for i in range(0,len(s),8):
			c=s[i:i+8];cr=c.rstrip(_E)
			if len(c)-len(cr)>1:sb.write(cr+_H)
			else:sb.write(c)
		return sb.getvalue()
	def get_file(self,fname):
		from os import listdir,stat
		if fname:
			self.fname=fname
			if fname in('.','..')or stat(fname)[0]&16384:self.content=["Directory '{}'".format(fname),'']+sorted(listdir(fname))
			else:
				if is_micropython:
					with open(fname)as f:self.content=f.readlines()
				else:
					with open(fname,errors='ignore')as f:self.content=f.readlines()
				tabs=_C
				for(i,l)in enumerate(self.content):self.content[i],tf=expandtabs(l.rstrip('\r\n\t '));tabs|=tf
				self.write_tabs=_D if tabs else'n'
	def put_file(self,fname):
		from os import remove,rename;tmpfile=fname+'.pyetmp'
		with open(tmpfile,'w')as f:
			for l in self.content:
				if self.write_tabs==_D:f.write(self.packtabs(l)+_G)
				else:f.write(l+_G)
		try:remove(fname)
		except:pass
		rename(tmpfile,fname)
def expandtabs(s):
	if _H in s:
		sb=StringIO();pos=0
		for c in s:
			if c==_H:sb.write(_E*(8-pos%8));pos+=8-pos%8
			else:sb.write(c);pos+=1
		return sb.getvalue(),_B
	else:return s,_C
def pye(*content,tab_size=4,undo=50,device=0):
	A='{!r}';gc.collect();index=0
	if content:
		slot=[]
		for f in content:
			slot.append(Editor(tab_size,undo))
			if type(f)==str and f:
				try:slot[index].get_file(f)
				except Exception as err:slot[index].message=A.format(err)
			elif type(f)==list and len(f)>0 and type(f[0])==str:slot[index].content=f
			index+=1
	else:slot=[Editor(tab_size,undo)];slot[0].get_file('.')
	Editor.init_tty(device)
	while _B:
		try:
			index%=len(slot);key=slot[index].edit_loop()
			if key==KEY_QUIT:
				if len(slot)==1:break
				del slot[index]
			elif key==KEY_GET:f=slot[index].line_edit('Open file: ','','_.-');slot.append(Editor(tab_size,undo));index=len(slot)-1;slot[index].get_file(f)
			elif key==KEY_NEXT:index+=1
		except Exception as err:slot[index].message=A.format(err)
	Editor.deinit_tty();Editor.yank_buffer=[];return slot[0].content if slot[0].fname==''else slot[0].fname
