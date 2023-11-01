# This file is a part of https://github.com/robert-hh/Micropython-Editor
A1=Exception
A0=staticmethod
n=ImportError
a=type
U=open
z=int
O='\t'
J='\n'
G=ord
Z='n'
Y=range
H='\x08'
W=min
V=max
N=' '
M='y'
L=False
K=True
I=''
F=None
C=len
import sys as E,gc
if E.platform in('linux','darwin'):import os,signal as b,tty,termios;P=K
else:P=L
if E.implementation.name=='micropython':D=K;from uio import StringIO as R;from ure import compile as m
else:D=L;A=lambda x:x;from _io import StringIO as R;from re import compile as m
AK=' V2.31 '
Q=A(0)
A2=A(11)
A3=A(13)
o=A(31)
p=A(30)
c=A(16)
d=A(3)
A4=A(65521)
A5=A(65522)
A6=A(65523)
A7=A(65524)
A8=A(65525)
A9=A(65526)
X=A(17)
e=A(10)
f=A(8)
g=A(127)
q=A(65527)
AA=A(19)
h=A(9)
i=A(21)
AB=A(6)
AC=A(7)
j=A(27)
r=A(28)
s=A(29)
AD=A(14)
AE=A(5)
AF=A(26)
t=A(24)
u=A(22)
k=A(4)
v=A(20)
w=A(2)
x=A(18)
AG=A(1)
S=A(15)
y=A(12)
T=A(23)
l=A(65532)
AH=A(65533)
AI=A(65534)
AJ=A(65535)
class B:
	KEYMAP={'\x1b[A':A2,'\x1b[1;2A':A8,'\x1b[B':A3,'\x1b[1;2B':A9,'\x1b[D':o,'\x1b[C':p,'\x1b[H':c,'\x1bOH':c,'\x1b[1~':c,'\x1b[F':d,'\x1bOF':d,'\x1b[4~':d,'\x1b[5~':A4,'\x1b[6~':A5,'\x1b[1;5D':A6,'\x1b[1;5C':A7,'\x03':k,'\r':e,'\x7f':f,'\x1b[3~':g,'\x1b[Z':i,'\x19':t,H:x,'\x12':x,'\x11':X,'\x1bq':X,J:e,'\x13':AA,'\x06':AB,'\x0e':AD,'\x07':AC,'\x05':AE,'\x1a':AF,O:h,'\x15':i,'\x18':t,'\x16':u,'\x04':k,'\x0c':y,'\x00':y,'\x14':v,'\x02':w,'\x01':AG,'\x17':T,'\x0f':S,'\x10':l,'\x1b[1;5A':r,'\x1b[1;5B':s,'\x1b[1;5H':v,'\x1b[1;5F':w,'\x1b[3;5~':q,'\x0b':AH,'\x1b[M':j};yank_buffer=[];find_pattern=I;case=Z;autoindent=M;replc_pattern=I;comment_char='# ';word_char='_\\'
	def __init__(A,tab_size,undo_limit):A.top_line=A.cur_line=A.row=A.col=A.margin=0;A.tab_size=tab_size;A.changed=I;A.message=A.fname=I;A.content=[I];A.undo=[];A.undo_limit=V(undo_limit,0);A.undo_zero=0;A.mark=F;A.write_tabs=Z
	if D and not P:
		def wr(A,s):E.stdout.write(s)
		def rd(A):return E.stdin.read(1)
		@A0
		def init_tty(device):
			try:from micropython import kbd_intr as A;A(-1)
			except n:pass
		@A0
		def deinit_tty():
			try:from micropython import kbd_intr as A;A(3)
			except n:pass
	def goto(A,row,col):A.wr('\x1b[{};{}H'.format(row+1,col+1))
	def clear_to_eol(A):A.wr('\x1b[0K')
	def cursor(A,onoff):A.wr('\x1b[?25h'if onoff else'\x1b[?25l')
	def hilite(A,mode):
		if mode==1:A.wr('\x1b[1;47m')
		elif mode==2:A.wr('\x1b[43m')
		else:A.wr('\x1b[0m')
	def mouse_reporting(A,onoff):A.wr('\x1b[?9h'if onoff else'\x1b[?9l')
	def scroll_region(A,stop):A.wr('\x1b[1;{}r'.format(stop)if stop else'\x1b[r')
	def scroll_up(C,scrolling):A=scrolling;B.scrbuf[A:]=B.scrbuf[:-A];B.scrbuf[:A]=[I]*A;C.goto(0,0);C.wr('\x1bM'*A)
	def scroll_down(C,scrolling):A=scrolling;B.scrbuf[:-A]=B.scrbuf[A:];B.scrbuf[-A:]=[I]*A;C.goto(B.height-1,0);C.wr(J*A)
	def get_screen_size(A):
		A.wr('\x1b[999;999H\x1b[6n');C=I;B=A.rd()
		while B!='R':C+=B;B=A.rd()
		return[z(A,10)for A in C.lstrip('\n\x1b[').split(';')]
	def redraw(A,flag):
		A.cursor(L);B.height,B.width=A.get_screen_size();B.height-=1;B.scrbuf=[(L,'\x00')]*B.height;A.row=W(B.height-1,A.row);A.scroll_region(B.height);A.mouse_reporting(K)
		if flag:A.message=AK
		if P and not D:b.signal(b.SIGWINCH,B.signal_handler)
		if D:
			gc.collect()
			if flag:A.message+='{} Bytes Memory available'.format(gc.mem_free())
	def get_input(A):
		while K:
			B=A.rd()
			if B=='\x1b':
				while K:
					B+=A.rd();C=B[-1]
					if C=='~'or C.isalpha()and C!='O':break
			if B in A.KEYMAP:
				C=A.KEYMAP[B]
				if C!=j:return C,F
				else:
					D=G(A.rd());E=G(A.rd())-33;H=G(A.rd())-33
					if D==97:return s,F
					elif D==96:return r,F
					else:return j,[E,H,D]
			elif G(B[0])>=32:return Q,B
	def display_window(A):
		A.cur_line=W(A.total_lines-1,V(A.cur_line,0));A.col=V(0,W(A.col,C(A.content[A.cur_line])))
		if A.col>=B.width+A.margin:A.margin=A.col-B.width+(B.width>>2)
		elif A.col<A.margin:A.margin=V(A.col-(B.width>>2),0)
		if not A.top_line<=A.cur_line<A.top_line+B.height:A.top_line=V(A.cur_line-A.row,0)
		A.row=A.cur_line-A.top_line;A.cursor(L);G=A.top_line;H,J=(-2,-1)if A.mark is F else A.line_range()
		for D in Y(B.height):
			if G==A.total_lines:
				if B.scrbuf[D]!=(L,I):A.goto(D,0);A.clear_to_eol();B.scrbuf[D]=L,I
			else:
				E=H<=G<J,A.content[G][A.margin:A.margin+B.width]
				if E!=B.scrbuf[D]:
					A.goto(D,0)
					if E[0]:A.hilite(2)
					A.wr(E[1])
					if C(E[1])<B.width:A.clear_to_eol()
					if E[0]:A.hilite(0)
					B.scrbuf[D]=E
				G+=1
		A.goto(B.height,0);A.hilite(1);A.wr('{}{} Row: {}/{} Col: {}  {}'.format(A.changed,A.fname,A.cur_line+1,A.total_lines,A.col+1,A.message)[:A.width-1]);A.clear_to_eol();A.hilite(0);A.goto(A.row,A.col-A.margin);A.cursor(K)
	def spaces(D,line,pos=F):B=pos;A=line;return C(A)-C(A.lstrip(N))if B is F else C(A[:B])-C(A[:B].rstrip(N))
	def line_range(A):return(A.mark,A.cur_line+1)if A.mark<A.cur_line else(A.cur_line,A.mark+1)
	def line_edit(E,prompt,default,zap=F):
		M=default;L=prompt;J=lambda msg:E.wr(msg+H*C(msg));E.goto(B.height,0);E.hilite(1);E.wr(L);E.wr(M);E.clear_to_eol();A=M;D=C(A)
		while K:
			G,I=E.get_input()
			if G==Q:
				if C(L)+C(A)<E.width-2:A=A[:D]+I+A[D:];E.wr(A[D]);D+=C(I);J(A[D:])
			elif G in(e,h):E.hilite(0);return A
			elif G in(X,k):E.hilite(0);return
			elif G==o:
				if D>0:E.wr(H);D-=1
			elif G==p:
				if D<C(A):E.wr(A[D]);D+=1
			elif G==c:E.wr(H*D);D=0
			elif G==d:E.wr(A[D:]);D=C(A)
			elif G==g:
				if D<C(A):A=A[:D]+A[D+1:];J(A[D:]+N)
			elif G==f:
				if D>0:A=A[:D-1]+A[D:];E.wr(H);D-=1;J(A[D:]+N)
			elif G==u:
				I=E.getsymbol(E.content[E.cur_line],E.col,zap)
				if I is not F:E.wr(H*D+N*C(A)+H*C(A));A=I;E.wr(A);D=C(A)
	def getsymbol(D,s,pos,zap):
		B=zap;A=pos
		if A<C(s)and B is not F:E=D.skip_while(s,A,B,-1);G=D.skip_while(s,A,B,1);return s[E+1:G]
	def issymbol(A,c,zap):return c.isalpha()or c.isdigit()or c in zap
	def skip_until(B,s,pos,zap,way):
		A=pos;D=-1 if way<0 else C(s)
		while A!=D and not B.issymbol(s[A],zap):A+=way
		return A
	def skip_while(B,s,pos,zap,way):
		A=pos;D=-1 if way<0 else C(s)
		while A!=D and B.issymbol(s[A],zap):A+=way
		return A
	def move_up(A):
		if A.cur_line>0:
			A.cur_line-=1
			if A.cur_line<A.top_line:A.scroll_up(1)
	def skip_up(A):
		if A.col==0 and A.cur_line>0:A.col=C(A.content[A.cur_line-1]);A.move_up();return K
		else:return L
	def move_down(A):
		if A.cur_line<A.total_lines-1:
			A.cur_line+=1
			if A.cur_line==A.top_line+B.height:A.scroll_down(1)
	def skip_down(A,l):
		if A.col>=C(l)and A.cur_line<A.total_lines-1:A.col=0;A.move_down();return K
		else:return L
	def find_in_file(A,pattern,col,end):
		E=col;D=pattern;B.find_pattern=D
		if B.case!=M:D=D.lower()
		try:J=m(D)
		except:A.message='Invalid pattern: '+D;return
		H=A.cur_line
		if E>C(A.content[H])or D[0]=='^'and E!=0:H,E=H+1,0
		for I in Y(H,end):
			F=A.content[I][E:]
			if B.case!=M:F=F.lower()
			G=J.search(F)
			if G:
				A.cur_line=I
				if D[-1:]=='$'and G.group(0)[-1:]!='$':A.col=E+C(F)-C(G.group(0))
				else:A.col=E+F.find(G.group(0))
				return C(G.group(0))
			E=0
		else:A.message=D+' not found (again)';return
	def undo_add(A,lnum,text,key,span=1):
		B=key;A.changed='*'
		if A.undo_limit>0 and(C(A.undo)==0 or B==Q or A.undo[-1][3]!=B or A.undo[-1][0]!=lnum):
			if C(A.undo)>=A.undo_limit:del A.undo[0];A.undo_zero-=1
			A.undo.append([lnum,span,text,B,A.col])
	def delete_lines(A,yank):
		D=A.line_range()
		if yank:B.yank_buffer=A.content[D[0]:D[1]]
		A.undo_add(D[0],A.content[D[0]:D[1]],Q,0);del A.content[D[0]:D[1]]
		if A.content==[]:A.content=[I];A.undo[-1][1]=1
		A.total_lines=C(A.content);A.cur_line=D[0];A.mark=F
	def handle_edit_keys(A,key,char):
		S=char;E=key;D=A.content[A.cur_line]
		if E==Q:A.mark=F;A.undo_add(A.cur_line,[D],32 if S==N else 65);A.content[A.cur_line]=D[:A.col]+S+D[A.col:];A.col+=C(S)
		elif E==A3:A.move_down()
		elif E==A2:A.move_up()
		elif E==o:
			if not A.skip_up():A.col-=1
		elif E==p:
			if not A.skip_down(D):A.col+=1
		elif E==A6:
			if A.skip_up():D=A.content[A.cur_line]
			T=A.skip_until(D,A.col-1,A.word_char,-1);A.col=A.skip_while(D,T,A.word_char,-1)+1
		elif E==A7:
			if A.skip_down(D):D=A.content[A.cur_line]
			T=A.skip_until(D,A.col,A.word_char,1);A.col=A.skip_while(D,T,A.word_char,1)
		elif E==g:
			if A.mark is not F:A.delete_lines(L)
			elif A.col<C(D):A.undo_add(A.cur_line,[D],g);A.content[A.cur_line]=D[:A.col]+D[A.col+1:]
			elif A.cur_line+1<A.total_lines:A.undo_add(A.cur_line,[D,A.content[A.cur_line+1]],Q);A.content[A.cur_line]=D+(A.content.pop(A.cur_line+1).lstrip()if B.autoindent==M and A.col>0 else A.content.pop(A.cur_line+1));A.total_lines-=1
		elif E==f:
			if A.mark is not F:A.delete_lines(L)
			elif A.col>0:A.undo_add(A.cur_line,[D],f);A.content[A.cur_line]=D[:A.col-1]+D[A.col:];A.col-=1
			elif A.cur_line>0:A.undo_add(A.cur_line-1,[A.content[A.cur_line-1],D],Q);A.col=C(A.content[A.cur_line-1]);A.content[A.cur_line-1]+=A.content.pop(A.cur_line);A.cur_line-=1;A.total_lines-=1
		elif E==q:
			if A.col<C(D):
				T=A.skip_while(D,A.col,A.word_char,1);T+=A.spaces(D[T:])
				if A.col<T:A.undo_add(A.cur_line,[D],q);A.content[A.cur_line]=D[:A.col]+D[T:]
		elif E==c:A.col=A.spaces(D)if A.col==0 else 0
		elif E==d:J=C(D.split(B.comment_char.strip())[0].rstrip());P=A.spaces(D);A.col=J if A.col>=C(D)and J>P else C(D)
		elif E==A4:A.cur_line-=B.height
		elif E==A5:A.cur_line+=B.height
		elif E==AB:
			U=A.line_edit('Find: ',B.find_pattern,'_')
			if U:A.find_in_file(U,A.col,A.total_lines);A.row=B.height>>1
		elif E==AD:
			if B.find_pattern:A.find_in_file(B.find_pattern,A.col+1,A.total_lines);A.row=B.height>>1
		elif E==AC:
			AK=A.line_edit('Goto Line: ',I)
			if AK:A.cur_line=z(AK)-1;A.row=B.height>>1
		elif E==v:A.cur_line=0
		elif E==w:A.cur_line=A.total_lines-1;A.row=B.height-1
		elif E==AG:
			U=A.line_edit('Autoindent {}, Search Case {}, Tabsize {}, Comment {}, Tabwrite {}: '.format(B.autoindent,B.case,A.tab_size,B.comment_char,A.write_tabs),I)
			try:
				R=[A.lstrip().lower()for A in U.split(',')]
				if R[0]:B.autoindent=M if R[0][0]==M else Z
				if R[1]:B.case=M if R[1][0]==M else Z
				if R[2]:A.tab_size=z(R[2])
				if R[3]:B.comment_char=R[3]
				if R[4]:A.write_tabs=M if R[4][0]==M else Z
			except:pass
		elif E==j:
			if S[1]<B.height:
				A.col=S[0]+A.margin;A.cur_line=S[1]+A.top_line
				if S[2]in(34,48):A.mark=A.cur_line if A.mark is F else F
		elif E==r:
			if A.top_line>0:A.top_line=V(A.top_line-3,0);A.cur_line=W(A.cur_line,A.top_line+B.height-1);A.scroll_up(3)
		elif E==s:
			if A.top_line+B.height<A.total_lines:A.top_line=W(A.top_line+3,A.total_lines-1);A.cur_line=V(A.cur_line,A.top_line);A.scroll_down(3)
		elif E==AH:
			if A.col<C(D):
				AL='<{[()]}>';AM=D[A.col];G=AL.find(AM)
				if G>=0:
					AP=AL[7-G];A0=0;a=1 if G<4 else-1;G=A.cur_line;b=A.col+a;AQ=A.total_lines if a>0 else-1
					while G!=AQ:
						AR=C(A.content[G])if a>0 else-1
						while b!=AR:
							if A.content[G][b]==AP:
								if A0==0:A.cur_line,A.col=G,b;return K
								else:A0-=1
							elif A.content[G][b]==AM:A0+=1
							b+=a
						G+=a;b=0 if a>0 else C(A.content[G])-1
					A.message='No match'
		elif E==y:A.mark=A.cur_line if A.mark is F else F
		elif E==A9:
			if A.mark is F:A.mark=A.cur_line
			else:A.move_down()
		elif E==A8:
			if A.mark is F:A.mark=A.cur_line
			else:A.move_up()
		elif E==e:
			A.mark=F;A.undo_add(A.cur_line,[D],Q,2);A.content[A.cur_line]=D[:A.col];J=0
			if B.autoindent==M:J=W(A.spaces(D),A.col)
			A.cur_line+=1;A.content[A.cur_line:A.cur_line]=[N*J+D[A.col:]];A.total_lines+=1;A.col=J
		elif E==h:
			if A.mark is F:A.undo_add(A.cur_line,[D],h);J=A.tab_size-A.col%A.tab_size;A.content[A.cur_line]=D[:A.col]+N*J+D[A.col:];A.col+=J
			else:
				H=A.line_range();A.undo_add(H[0],A.content[H[0]:H[1]],AI,H[1]-H[0])
				for G in Y(H[0],H[1]):
					if C(A.content[G])>0:A.content[G]=N*(A.tab_size-A.spaces(A.content[G])%A.tab_size)+A.content[G]
		elif E==i:
			if A.mark is F:
				J=W((A.col-1)%A.tab_size+1,A.spaces(D,A.col))
				if J>0:A.undo_add(A.cur_line,[D],i);A.content[A.cur_line]=D[:A.col-J]+D[A.col:];A.col-=J
			else:
				H=A.line_range();A.undo_add(H[0],A.content[H[0]:H[1]],AJ,H[1]-H[0])
				for G in Y(H[0],H[1]):
					P=A.spaces(A.content[G])
					if P>0:A.content[G]=A.content[G][(P-1)%A.tab_size+1:]
		elif E==x:
			AN=0;U=A.line_edit('Replace: ',B.find_pattern,'_')
			if U:
				m=A.line_edit('With: ',B.replc_pattern,'_')
				if m is not F:
					B.replc_pattern=m;n=I;AS,AT=A.cur_line,A.col
					if A.mark is not F:A.cur_line,AO=A.line_range();A.col=0
					else:AO=A.total_lines
					A.message='Replace (yes/No/all/quit) ? '
					while K:
						J=A.find_in_file(U,A.col,AO)
						if J is not F:
							if n!='a':A.display_window();E,S=A.get_input();n=S.lower()
							if n=='q'or E==X:break
							elif n in('a',M):A.undo_add(A.cur_line,[A.content[A.cur_line]],Q);A.content[A.cur_line]=A.content[A.cur_line][:A.col]+m+A.content[A.cur_line][A.col+J:];A.col+=C(m)+(J==0);AN+=1
							else:A.col+=1
						else:break
					A.cur_line,A.col=AS,AT;A.message="'{}' replaced {} times".format(U,AN)
		elif E==t:
			if A.mark is not F:A.delete_lines(K)
		elif E==k:
			if A.mark is not F:H=A.line_range();B.yank_buffer=A.content[H[0]:H[1]];A.mark=F
		elif E==u:
			if B.yank_buffer:
				if A.mark is not F:A.delete_lines(L)
				A.undo_add(A.cur_line,F,Q,-C(B.yank_buffer));A.content[A.cur_line:A.cur_line]=B.yank_buffer;A.total_lines+=C(B.yank_buffer)
		elif E==AA:
			A1=A.line_edit('Save File: ',A.fname)
			if A1:A.put_file(A1);A.changed=I;A.undo_zero=C(A.undo);A.fname=A1
		elif E==AF:
			if C(A.undo)>0:
				O=A.undo.pop(-1)
				if not O[3]in(AI,AJ,l):A.cur_line=O[0]
				A.col=O[4]
				if O[1]>=0:
					if O[0]<A.total_lines:A.content[O[0]:O[0]+O[1]]=O[2]
					else:A.content+=O[2]
				else:del A.content[O[0]:O[0]-O[1]]
				A.total_lines=C(A.content)
				if C(A.undo)==A.undo_zero:A.changed=I
				A.mark=F
		elif E==l:
			if A.mark is F:H=A.cur_line,A.cur_line+1
			else:H=A.line_range()
			A.undo_add(H[0],A.content[H[0]:H[1]],l,H[1]-H[0]);J=C(B.comment_char)
			for G in Y(H[0],H[1]):
				P=A.spaces(A.content[G])
				if A.content[G][P:P+J]==B.comment_char:A.content[G]=P*N+A.content[G][P+J:]
				else:A.content[G]=P*N+B.comment_char+A.content[G][P:]
		elif E==AE:A.redraw(K)
	def edit_loop(A):
		if not A.content:A.content=[I]
		A.total_lines=C(A.content);A.redraw(A.message==I)
		while K:
			A.display_window();D,F=A.get_input();A.message=I
			if D==X:
				if A.changed:
					E=A.line_edit('Content changed! Quit without saving (y/N)? ','N')
					if not E or E[0].upper()!='Y':continue
				A.scroll_region(0);A.mouse_reporting(L);A.goto(B.height,0);A.clear_to_eol();A.undo=[];return D
			elif D in(T,S):return D
			else:A.handle_edit_keys(D,F)
	def packtabs(F,s):
		A=R()
		for D in Y(0,C(s),8):
			B=s[D:D+8];E=B.rstrip(N)
			if C(B)-C(E)>1:A.write(E+O)
			else:A.write(B)
		return A.getvalue()
	def get_file(B,fname):
		A=fname;from os import listdir as F,stat
		if A:
			B.fname=A
			if A in('.','..')or stat(A)[0]&16384:B.content=["Directory '{}'".format(A),I]+sorted(F(A))
			else:
				if D:
					with U(A)as C:B.content=C.readlines()
				else:
					with U(A,errors='ignore')as C:B.content=C.readlines()
				E=L
				for(G,H)in enumerate(B.content):B.content[G],J=AL(H.rstrip('\r\n\t '));E|=J
				B.write_tabs=M if E else Z
	def put_file(A,fname):
		B=fname;from os import remove as F,rename as G;C=B+'.pyetmp'
		with U(C,'w')as D:
			for E in A.content:
				if A.write_tabs==M:D.write(A.packtabs(E)+J)
				else:D.write(E+J)
		try:F(B)
		except:pass
		G(C,B)
def AL(s):
	if O in s:
		B=R();A=0
		for C in s:
			if C==O:B.write(N*(8-A%8));A+=8-A%8
			else:B.write(C);A+=1
		return B.getvalue(),K
	else:return s,L
def AM(*L,tab_size=4,undo=50,device=0):
	M='{!r}';G=undo;F=tab_size;gc.collect();D=0
	if L:
		A=[]
		for E in L:
			A.append(B(F,G))
			if a(E)==str and E:
				try:A[D].get_file(E)
				except A1 as H:A[D].message=M.format(H)
			elif a(E)==list and C(E)>0 and a(E[0])==str:A[D].content=E
			D+=1
	else:A=[B(F,G)];A[0].get_file('.')
	B.init_tty(device)
	while K:
		try:
			D%=C(A);J=A[D].edit_loop()
			if J==X:
				if C(A)==1:break
				del A[D]
			elif J==S:E=A[D].line_edit('Open file: ',I,'_.-');A.append(B(F,G));D=C(A)-1;A[D].get_file(E)
			elif J==T:D+=1
		except A1 as H:A[D].message=M.format(H)
	B.deinit_tty();B.yank_buffer=[];return A[0].content if A[0].fname==I else A[0].fname
