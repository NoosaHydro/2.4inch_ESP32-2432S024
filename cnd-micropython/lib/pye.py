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
	def __init__(A,tab_size,undo_limit):A.top_line=A.cur_line=A.row=A.col=A.margin=0;A.tab_size=tab_size;A.changed='';A.message=A.fname='';A.content=[''];A.undo=[];A.undo_limit=max(undo_limit,0);A.undo_zero=0;A.mark=_A;A.write_tabs='n'
	if is_micropython and not is_linux:
		def wr(A,s):sys.stdout.write(s)
		def rd(A):return sys.stdin.read(1)
		@staticmethod
		def init_tty(device):
			try:from micropython import kbd_intr as A;A(-1)
			except ImportError:pass
		@staticmethod
		def deinit_tty():
			try:from micropython import kbd_intr as A;A(3)
			except ImportError:pass
	def goto(A,row,col):A.wr('\x1b[{};{}H'.format(row+1,col+1))
	def clear_to_eol(A):A.wr('\x1b[0K')
	def cursor(A,onoff):A.wr('\x1b[?25h'if onoff else'\x1b[?25l')
	def hilite(A,mode):
		if mode==1:A.wr('\x1b[1;47m')
		elif mode==2:A.wr('\x1b[43m')
		else:A.wr('\x1b[0m')
	def mouse_reporting(A,onoff):A.wr('\x1b[?9h'if onoff else'\x1b[?9l')
	def scroll_region(A,stop):A.wr('\x1b[1;{}r'.format(stop)if stop else'\x1b[r')
	def scroll_up(B,scrolling):A=scrolling;Editor.scrbuf[A:]=Editor.scrbuf[:-A];Editor.scrbuf[:A]=['']*A;B.goto(0,0);B.wr('\x1bM'*A)
	def scroll_down(B,scrolling):A=scrolling;Editor.scrbuf[:-A]=Editor.scrbuf[A:];Editor.scrbuf[-A:]=['']*A;B.goto(Editor.height-1,0);B.wr(_G*A)
	def get_screen_size(A):
		A.wr('\x1b[999;999H\x1b[6n');C='';B=A.rd()
		while B!='R':C+=B;B=A.rd()
		return[int(A,10)for A in C.lstrip('\n\x1b[').split(';')]
	def redraw(A,flag):
		A.cursor(_C);Editor.height,Editor.width=A.get_screen_size();Editor.height-=1;Editor.scrbuf=[(_C,'\x00')]*Editor.height;A.row=min(Editor.height-1,A.row);A.scroll_region(Editor.height);A.mouse_reporting(_B)
		if flag:A.message=PYE_VERSION
		if is_linux and not is_micropython:signal.signal(signal.SIGWINCH,Editor.signal_handler)
		if is_micropython:
			gc.collect()
			if flag:A.message+='{} Bytes Memory available'.format(gc.mem_free())
	def get_input(A):
		while _B:
			B=A.rd()
			if B=='\x1b':
				while _B:
					B+=A.rd();C=B[-1]
					if C=='~'or C.isalpha()and C!='O':break
			if B in A.KEYMAP:
				C=A.KEYMAP[B]
				if C!=KEY_MOUSE:return C,_A
				else:
					D=ord(A.rd());E=ord(A.rd())-33;F=ord(A.rd())-33
					if D==97:return KEY_SCRLDN,_A
					elif D==96:return KEY_SCRLUP,_A
					else:return KEY_MOUSE,[E,F,D]
			elif ord(B[0])>=32:return KEY_NONE,B
	def display_window(A):
		A.cur_line=min(A.total_lines-1,max(A.cur_line,0));A.col=max(0,min(A.col,len(A.content[A.cur_line])))
		if A.col>=Editor.width+A.margin:A.margin=A.col-Editor.width+(Editor.width>>2)
		elif A.col<A.margin:A.margin=max(A.col-(Editor.width>>2),0)
		if not A.top_line<=A.cur_line<A.top_line+Editor.height:A.top_line=max(A.cur_line-A.row,0)
		A.row=A.cur_line-A.top_line;A.cursor(_C);D=A.top_line;E,F=(-2,-1)if A.mark is _A else A.line_range()
		for B in range(Editor.height):
			if D==A.total_lines:
				if Editor.scrbuf[B]!=(_C,''):A.goto(B,0);A.clear_to_eol();Editor.scrbuf[B]=_C,''
			else:
				C=E<=D<F,A.content[D][A.margin:A.margin+Editor.width]
				if C!=Editor.scrbuf[B]:
					A.goto(B,0)
					if C[0]:A.hilite(2)
					A.wr(C[1])
					if len(C[1])<Editor.width:A.clear_to_eol()
					if C[0]:A.hilite(0)
					Editor.scrbuf[B]=C
				D+=1
		A.goto(Editor.height,0);A.hilite(1);A.wr('{}{} Row: {}/{} Col: {}  {}'.format(A.changed,A.fname,A.cur_line+1,A.total_lines,A.col+1,A.message)[:A.width-1]);A.clear_to_eol();A.hilite(0);A.goto(A.row,A.col-A.margin);A.cursor(_B)
	def spaces(C,line,pos=_A):B=pos;A=line;return len(A)-len(A.lstrip(_E))if B is _A else len(A[:B])-len(A[:B].rstrip(_E))
	def line_range(A):return(A.mark,A.cur_line+1)if A.mark<A.cur_line else(A.cur_line,A.mark+1)
	def line_edit(C,prompt,default,zap=_A):
		H=default;G=prompt;F=lambda msg:C.wr(msg+_F*len(msg));C.goto(Editor.height,0);C.hilite(1);C.wr(G);C.wr(H);C.clear_to_eol();A=H;B=len(A)
		while _B:
			D,E=C.get_input()
			if D==KEY_NONE:
				if len(G)+len(A)<C.width-2:A=A[:B]+E+A[B:];C.wr(A[B]);B+=len(E);F(A[B:])
			elif D in(KEY_ENTER,KEY_TAB):C.hilite(0);return A
			elif D in(KEY_QUIT,KEY_DUP):C.hilite(0);return
			elif D==KEY_LEFT:
				if B>0:C.wr(_F);B-=1
			elif D==KEY_RIGHT:
				if B<len(A):C.wr(A[B]);B+=1
			elif D==KEY_HOME:C.wr(_F*B);B=0
			elif D==KEY_END:C.wr(A[B:]);B=len(A)
			elif D==KEY_DELETE:
				if B<len(A):A=A[:B]+A[B+1:];F(A[B:]+_E)
			elif D==KEY_BACKSPACE:
				if B>0:A=A[:B-1]+A[B:];C.wr(_F);B-=1;F(A[B:]+_E)
			elif D==KEY_ZAP:
				E=C.getsymbol(C.content[C.cur_line],C.col,zap)
				if E is not _A:C.wr(_F*B+_E*len(A)+_F*len(A));A=E;C.wr(A);B=len(A)
	def getsymbol(C,s,pos,zap):
		B=zap;A=pos
		if A<len(s)and B is not _A:D=C.skip_while(s,A,B,-1);E=C.skip_while(s,A,B,1);return s[D+1:E]
	def issymbol(A,c,zap):return c.isalpha()or c.isdigit()or c in zap
	def skip_until(B,s,pos,zap,way):
		A=pos;C=-1 if way<0 else len(s)
		while A!=C and not B.issymbol(s[A],zap):A+=way
		return A
	def skip_while(B,s,pos,zap,way):
		A=pos;C=-1 if way<0 else len(s)
		while A!=C and B.issymbol(s[A],zap):A+=way
		return A
	def move_up(A):
		if A.cur_line>0:
			A.cur_line-=1
			if A.cur_line<A.top_line:A.scroll_up(1)
	def skip_up(A):
		if A.col==0 and A.cur_line>0:A.col=len(A.content[A.cur_line-1]);A.move_up();return _B
		else:return _C
	def move_down(A):
		if A.cur_line<A.total_lines-1:
			A.cur_line+=1
			if A.cur_line==A.top_line+Editor.height:A.scroll_down(1)
	def skip_down(A,l):
		if A.col>=len(l)and A.cur_line<A.total_lines-1:A.col=0;A.move_down();return _B
		else:return _C
	def find_in_file(A,pattern,col,end):
		C=col;B=pattern;Editor.find_pattern=B
		if Editor.case!=_D:B=B.lower()
		try:H=re_compile(B)
		except:A.message='Invalid pattern: '+B;return
		F=A.cur_line
		if C>len(A.content[F])or B[0]=='^'and C!=0:F,C=F+1,0
		for G in range(F,end):
			D=A.content[G][C:]
			if Editor.case!=_D:D=D.lower()
			E=H.search(D)
			if E:
				A.cur_line=G
				if B[-1:]=='$'and E.group(0)[-1:]!='$':A.col=C+len(D)-len(E.group(0))
				else:A.col=C+D.find(E.group(0))
				return len(E.group(0))
			C=0
		else:A.message=B+' not found (again)';return
	def undo_add(A,lnum,text,key,span=1):
		B=key;A.changed='*'
		if A.undo_limit>0 and(len(A.undo)==0 or B==KEY_NONE or A.undo[-1][3]!=B or A.undo[-1][0]!=lnum):
			if len(A.undo)>=A.undo_limit:del A.undo[0];A.undo_zero-=1
			A.undo.append([lnum,span,text,B,A.col])
	def delete_lines(A,yank):
		B=A.line_range()
		if yank:Editor.yank_buffer=A.content[B[0]:B[1]]
		A.undo_add(B[0],A.content[B[0]:B[1]],KEY_NONE,0);del A.content[B[0]:B[1]]
		if A.content==[]:A.content=[''];A.undo[-1][1]=1
		A.total_lines=len(A.content);A.cur_line=B[0];A.mark=_A
	def handle_edit_keys(A,key,char):
		S='_';J=char;C=key;B=A.content[A.cur_line]
		if C==KEY_NONE:A.mark=_A;A.undo_add(A.cur_line,[B],32 if J==_E else 65);A.content[A.cur_line]=B[:A.col]+J+B[A.col:];A.col+=len(J)
		elif C==KEY_DOWN:A.move_down()
		elif C==KEY_UP:A.move_up()
		elif C==KEY_LEFT:
			if not A.skip_up():A.col-=1
		elif C==KEY_RIGHT:
			if not A.skip_down(B):A.col+=1
		elif C==KEY_WORD_LEFT:
			if A.skip_up():B=A.content[A.cur_line]
			K=A.skip_until(B,A.col-1,A.word_char,-1);A.col=A.skip_while(B,K,A.word_char,-1)+1
		elif C==KEY_WORD_RIGHT:
			if A.skip_down(B):B=A.content[A.cur_line]
			K=A.skip_until(B,A.col,A.word_char,1);A.col=A.skip_while(B,K,A.word_char,1)
		elif C==KEY_DELETE:
			if A.mark is not _A:A.delete_lines(_C)
			elif A.col<len(B):A.undo_add(A.cur_line,[B],KEY_DELETE);A.content[A.cur_line]=B[:A.col]+B[A.col+1:]
			elif A.cur_line+1<A.total_lines:A.undo_add(A.cur_line,[B,A.content[A.cur_line+1]],KEY_NONE);A.content[A.cur_line]=B+(A.content.pop(A.cur_line+1).lstrip()if Editor.autoindent==_D and A.col>0 else A.content.pop(A.cur_line+1));A.total_lines-=1
		elif C==KEY_BACKSPACE:
			if A.mark is not _A:A.delete_lines(_C)
			elif A.col>0:A.undo_add(A.cur_line,[B],KEY_BACKSPACE);A.content[A.cur_line]=B[:A.col-1]+B[A.col:];A.col-=1
			elif A.cur_line>0:A.undo_add(A.cur_line-1,[A.content[A.cur_line-1],B],KEY_NONE);A.col=len(A.content[A.cur_line-1]);A.content[A.cur_line-1]+=A.content.pop(A.cur_line);A.cur_line-=1;A.total_lines-=1
		elif C==KEY_DEL_WORD:
			if A.col<len(B):
				K=A.skip_while(B,A.col,A.word_char,1);K+=A.spaces(B[K:])
				if A.col<K:A.undo_add(A.cur_line,[B],KEY_DEL_WORD);A.content[A.cur_line]=B[:A.col]+B[K:]
		elif C==KEY_HOME:A.col=A.spaces(B)if A.col==0 else 0
		elif C==KEY_END:F=len(B.split(Editor.comment_char.strip())[0].rstrip());H=A.spaces(B);A.col=F if A.col>=len(B)and F>H else len(B)
		elif C==KEY_PGUP:A.cur_line-=Editor.height
		elif C==KEY_PGDN:A.cur_line+=Editor.height
		elif C==KEY_FIND:
			L=A.line_edit('Find: ',Editor.find_pattern,S)
			if L:A.find_in_file(L,A.col,A.total_lines);A.row=Editor.height>>1
		elif C==KEY_FIND_AGAIN:
			if Editor.find_pattern:A.find_in_file(Editor.find_pattern,A.col+1,A.total_lines);A.row=Editor.height>>1
		elif C==KEY_GOTO:
			T=A.line_edit('Goto Line: ','')
			if T:A.cur_line=int(T)-1;A.row=Editor.height>>1
		elif C==KEY_FIRST:A.cur_line=0
		elif C==KEY_LAST:A.cur_line=A.total_lines-1;A.row=Editor.height-1
		elif C==KEY_TOGGLE:
			L=A.line_edit('Autoindent {}, Search Case {}, Tabsize {}, Comment {}, Tabwrite {}: '.format(Editor.autoindent,Editor.case,A.tab_size,Editor.comment_char,A.write_tabs),'')
			try:
				I=[A.lstrip().lower()for A in L.split(',')]
				if I[0]:Editor.autoindent=_D if I[0][0]==_D else'n'
				if I[1]:Editor.case=_D if I[1][0]==_D else'n'
				if I[2]:A.tab_size=int(I[2])
				if I[3]:Editor.comment_char=I[3]
				if I[4]:A.write_tabs=_D if I[4][0]==_D else'n'
			except:pass
		elif C==KEY_MOUSE:
			if J[1]<Editor.height:
				A.col=J[0]+A.margin;A.cur_line=J[1]+A.top_line
				if J[2]in(34,48):A.mark=A.cur_line if A.mark is _A else _A
		elif C==KEY_SCRLUP:
			if A.top_line>0:A.top_line=max(A.top_line-3,0);A.cur_line=min(A.cur_line,A.top_line+Editor.height-1);A.scroll_up(3)
		elif C==KEY_SCRLDN:
			if A.top_line+Editor.height<A.total_lines:A.top_line=min(A.top_line+3,A.total_lines-1);A.cur_line=max(A.cur_line,A.top_line);A.scroll_down(3)
		elif C==KEY_MATCH:
			if A.col<len(B):
				U='<{[()]}>';V=B[A.col];D=U.find(V)
				if D>=0:
					Y=U[7-D];Q=0;M=1 if D<4 else-1;D=A.cur_line;N=A.col+M;Z=A.total_lines if M>0 else-1
					while D!=Z:
						a=len(A.content[D])if M>0 else-1
						while N!=a:
							if A.content[D][N]==Y:
								if Q==0:A.cur_line,A.col=D,N;return _B
								else:Q-=1
							elif A.content[D][N]==V:Q+=1
							N+=M
						D+=M;N=0 if M>0 else len(A.content[D])-1
					A.message='No match'
		elif C==KEY_MARK:A.mark=A.cur_line if A.mark is _A else _A
		elif C==KEY_SHIFT_DOWN:
			if A.mark is _A:A.mark=A.cur_line
			else:A.move_down()
		elif C==KEY_SHIFT_UP:
			if A.mark is _A:A.mark=A.cur_line
			else:A.move_up()
		elif C==KEY_ENTER:
			A.mark=_A;A.undo_add(A.cur_line,[B],KEY_NONE,2);A.content[A.cur_line]=B[:A.col];F=0
			if Editor.autoindent==_D:F=min(A.spaces(B),A.col)
			A.cur_line+=1;A.content[A.cur_line:A.cur_line]=[_E*F+B[A.col:]];A.total_lines+=1;A.col=F
		elif C==KEY_TAB:
			if A.mark is _A:A.undo_add(A.cur_line,[B],KEY_TAB);F=A.tab_size-A.col%A.tab_size;A.content[A.cur_line]=B[:A.col]+_E*F+B[A.col:];A.col+=F
			else:
				E=A.line_range();A.undo_add(E[0],A.content[E[0]:E[1]],KEY_INDENT,E[1]-E[0])
				for D in range(E[0],E[1]):
					if len(A.content[D])>0:A.content[D]=_E*(A.tab_size-A.spaces(A.content[D])%A.tab_size)+A.content[D]
		elif C==KEY_BACKTAB:
			if A.mark is _A:
				F=min((A.col-1)%A.tab_size+1,A.spaces(B,A.col))
				if F>0:A.undo_add(A.cur_line,[B],KEY_BACKTAB);A.content[A.cur_line]=B[:A.col-F]+B[A.col:];A.col-=F
			else:
				E=A.line_range();A.undo_add(E[0],A.content[E[0]:E[1]],KEY_UNDENT,E[1]-E[0])
				for D in range(E[0],E[1]):
					H=A.spaces(A.content[D])
					if H>0:A.content[D]=A.content[D][(H-1)%A.tab_size+1:]
		elif C==KEY_REPLC:
			W=0;L=A.line_edit('Replace: ',Editor.find_pattern,S)
			if L:
				O=A.line_edit('With: ',Editor.replc_pattern,S)
				if O is not _A:
					Editor.replc_pattern=O;P='';b,c=A.cur_line,A.col
					if A.mark is not _A:A.cur_line,X=A.line_range();A.col=0
					else:X=A.total_lines
					A.message='Replace (yes/No/all/quit) ? '
					while _B:
						F=A.find_in_file(L,A.col,X)
						if F is not _A:
							if P!='a':A.display_window();C,J=A.get_input();P=J.lower()
							if P=='q'or C==KEY_QUIT:break
							elif P in('a',_D):A.undo_add(A.cur_line,[A.content[A.cur_line]],KEY_NONE);A.content[A.cur_line]=A.content[A.cur_line][:A.col]+O+A.content[A.cur_line][A.col+F:];A.col+=len(O)+(F==0);W+=1
							else:A.col+=1
						else:break
					A.cur_line,A.col=b,c;A.message="'{}' replaced {} times".format(L,W)
		elif C==KEY_YANK:
			if A.mark is not _A:A.delete_lines(_B)
		elif C==KEY_DUP:
			if A.mark is not _A:E=A.line_range();Editor.yank_buffer=A.content[E[0]:E[1]];A.mark=_A
		elif C==KEY_ZAP:
			if Editor.yank_buffer:
				if A.mark is not _A:A.delete_lines(_C)
				A.undo_add(A.cur_line,_A,KEY_NONE,-len(Editor.yank_buffer));A.content[A.cur_line:A.cur_line]=Editor.yank_buffer;A.total_lines+=len(Editor.yank_buffer)
		elif C==KEY_WRITE:
			R=A.line_edit('Save File: ',A.fname)
			if R:A.put_file(R);A.changed='';A.undo_zero=len(A.undo);A.fname=R
		elif C==KEY_UNDO:
			if len(A.undo)>0:
				G=A.undo.pop(-1)
				if not G[3]in(KEY_INDENT,KEY_UNDENT,KEY_COMMENT):A.cur_line=G[0]
				A.col=G[4]
				if G[1]>=0:
					if G[0]<A.total_lines:A.content[G[0]:G[0]+G[1]]=G[2]
					else:A.content+=G[2]
				else:del A.content[G[0]:G[0]-G[1]]
				A.total_lines=len(A.content)
				if len(A.undo)==A.undo_zero:A.changed=''
				A.mark=_A
		elif C==KEY_COMMENT:
			if A.mark is _A:E=A.cur_line,A.cur_line+1
			else:E=A.line_range()
			A.undo_add(E[0],A.content[E[0]:E[1]],KEY_COMMENT,E[1]-E[0]);F=len(Editor.comment_char)
			for D in range(E[0],E[1]):
				H=A.spaces(A.content[D])
				if A.content[D][H:H+F]==Editor.comment_char:A.content[D]=H*_E+A.content[D][H+F:]
				else:A.content[D]=H*_E+Editor.comment_char+A.content[D][H:]
		elif C==KEY_REDRAW:A.redraw(_B)
	def edit_loop(A):
		if not A.content:A.content=['']
		A.total_lines=len(A.content);A.redraw(A.message=='')
		while _B:
			A.display_window();B,D=A.get_input();A.message=''
			if B==KEY_QUIT:
				if A.changed:
					C=A.line_edit('Content changed! Quit without saving (y/N)? ','N')
					if not C or C[0].upper()!='Y':continue
				A.scroll_region(0);A.mouse_reporting(_C);A.goto(Editor.height,0);A.clear_to_eol();A.undo=[];return B
			elif B in(KEY_NEXT,KEY_GET):return B
			else:A.handle_edit_keys(B,D)
	def packtabs(E,s):
		A=StringIO()
		for C in range(0,len(s),8):
			B=s[C:C+8];D=B.rstrip(_E)
			if len(B)-len(D)>1:A.write(D+_H)
			else:A.write(B)
		return A.getvalue()
	def get_file(B,fname):
		A=fname;from os import listdir as E,stat
		if A:
			B.fname=A
			if A in('.','..')or stat(A)[0]&16384:B.content=["Directory '{}'".format(A),'']+sorted(E(A))
			else:
				if is_micropython:
					with open(A)as C:B.content=C.readlines()
				else:
					with open(A,errors='ignore')as C:B.content=C.readlines()
				D=_C
				for(F,G)in enumerate(B.content):B.content[F],H=expandtabs(G.rstrip('\r\n\t '));D|=H
				B.write_tabs=_D if D else'n'
	def put_file(A,fname):
		B=fname;from os import remove as F,rename as G;C=B+'.pyetmp'
		with open(C,'w')as D:
			for E in A.content:
				if A.write_tabs==_D:D.write(A.packtabs(E)+_G)
				else:D.write(E+_G)
		try:F(B)
		except:pass
		G(C,B)
def expandtabs(s):
	if _H in s:
		B=StringIO();A=0
		for C in s:
			if C==_H:B.write(_E*(8-A%8));A+=8-A%8
			else:B.write(C);A+=1
		return B.getvalue(),_B
	else:return s,_C
def pye(*H,tab_size=4,undo=50,device=0):
	I='{!r}';E=undo;D=tab_size;gc.collect();B=0
	if H:
		A=[]
		for C in H:
			A.append(Editor(D,E))
			if type(C)==str and C:
				try:A[B].get_file(C)
				except Exception as F:A[B].message=I.format(F)
			elif type(C)==list and len(C)>0 and type(C[0])==str:A[B].content=C
			B+=1
	else:A=[Editor(D,E)];A[0].get_file('.')
	Editor.init_tty(device)
	while _B:
		try:
			B%=len(A);G=A[B].edit_loop()
			if G==KEY_QUIT:
				if len(A)==1:break
				del A[B]
			elif G==KEY_GET:C=A[B].line_edit('Open file: ','','_.-');A.append(Editor(D,E));B=len(A)-1;A[B].get_file(C)
			elif G==KEY_NEXT:B+=1
		except Exception as F:A[B].message=I.format(F)
	Editor.deinit_tty();Editor.yank_buffer=[];return A[0].content if A[0].fname==''else A[0].fname
