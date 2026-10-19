10 REM ==== MOON MISSION - title screen and mission menu ====
20 REM Needs MOONBG.PIC, EARTH.SPR, TITLE.SPR on the current drive
30 DEFINT A-Z: KEY OFF: CLS
40 EX = 112: EY = 33: HT = 126: SH = 82
50 Y = 0: K = 0: S = 1: NM = 2: MI = 1: NMU = 0: A$ = "": DT! = .2: T0! = 0
60 DIM E(986), T(682), M$(2), MU$(12)
70 M$(1) = "MOON LANDING": M$(2) = "EXIT TO DOS"
80 GOSUB 5000
100 REM ---- load art with the display switched off ----
110 SCREEN 1, 0: COLOR 0, 1: CLS
120 OUT &H3D8, &H6
130 DEF SEG = &HB800: BLOAD "MOONBG.PIC", 0: DEF SEG
140 BLOAD "EARTH.SPR", VARPTR(E(0))
150 BLOAD "TITLE.SPR", VARPTR(T(0))
170 OUT &H3D8, &HE: OUT &H3D9, 0
180 IF SK% = 1 THEN MI = NMU + 1: GOTO 400
200 REM ---- earthrise: draw only the rows above the horizon ----
210 GOSUB 900
220 T0! = TIMER
230 FOR K = 1 TO HT - EY
240 Y = HT - K
250 IF K < SH THEN E(1) = K ELSE E(1) = SH
255 PUT (EX, Y), E, PSET
260 GOSUB 900
270 IF INKEY$ <> "" THEN GOTO 400
280 IF TIMER < T0! + K * DT! THEN GOTO 260
290 NEXT K
400 REM ---- title and menu ----
410 LINE (EX, EY)-(EX + 95, HT - 1), 0, BF: E(1) = SH: PUT (EX, EY), E, PSET
420 PUT (24, 8), T, PSET
430 LINE (72, 146)-(247, 197), 0, BF: LINE (72, 146)-(247, 197), 1, B
440 LOCATE 20, 12: PRINT "- SELECT MISSION -";
450 FOR K = 1 TO NM: LOCATE 20 + 2 * K, 15: PRINT M$(K);: NEXT K
460 GOSUB 600
470 GOSUB 900: A$ = INKEY$: IF A$ = "" THEN 470
480 IF A$ = CHR$(0) + "H" AND S > 1 THEN S = S - 1: GOSUB 600
490 IF A$ = CHR$(0) + "P" AND S < NM THEN S = S + 1: GOSUB 600
500 IF A$ >= "1" AND A$ <= CHR$(48 + NM) THEN S = ASC(A$) - 48: GOSUB 600: A$ = CHR$(13)
510 IF A$ = CHR$(27) THEN S = NM: A$ = CHR$(13)
520 IF A$ <> CHR$(13) THEN 470
530 ON S GOTO 700, 800
600 REM ---- draw selection box ----
610 FOR K = 1 TO NM
620 LINE (108, 150 + 16 * K)-(211, 161 + 16 * K), -2 * (K = S), B
630 NEXT K: RETURN
700 REM ---- moon landing ----
710 CHAIN "LANDER"
800 REM ---- exit ----
810 SCREEN 0, 0: WIDTH 80: SYSTEM
900 REM ---- feed music a few notes at a time so PLAY never blocks ----
910 IF MI <= NMU THEN IF PLAY(0) < 4 THEN PLAY MU$(MI): MI = MI + 1
920 RETURN
5000 REM ---- Also sprach Zarathustra (opening) ----
5010 FOR K = 1 TO 9: READ MU$(K): NEXT K: NMU = 9: RETURN
5020 DATA "MBT100O1C1O3L4C2G2", "O4C2.E16E-1"
5030 DATA "O2L8CO1GO2CO1G", "O2CO1GO2CO1GO2C4"
5040 DATA "O3L4C2G2O4C2.E-16E1"
5050 DATA "O2L8CO1GO2CO1G", "O2CO1GO2CO1GO2C4"
5060 DATA "O3L4C2G2O4C2.", "A1B4O5C1."
