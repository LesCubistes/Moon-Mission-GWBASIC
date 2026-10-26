10 REM ==== MOON MISSION - START disk: title screen, high scores, mission menu ====
20 REM Needs MOONBG.PIC, EARTH.SPR, TITLE.SPR here; each mission lives on its own disk in drive B:
25 COMMON SK%, LS%, LD$
30 DEFINT A-Z: KEY OFF: CLS
40 EX = 112: EY = 33: HT = 126: SH = 82
50 Y = 0: K = 0: S = 1: NM = 2: MI = 1: NMU = 0: A$ = "": DT! = .2: T0! = 0: KP = 0: HR = 0: HE = 0: I = 0: LD$ = "B:": P$ = "": TY = 0
52 DEF SEG = &H40: I = PEEK(&H10): DEF SEG: IF (I AND &HC1) = 1 THEN LD$ = "A:": REM only one floppy drive: the mission disk goes in A: too
53 DEF SEG = &HF000: TY = (PEEK(49152!) = &H21): DEF SEG: REM a Tandy 1000 needs its own palette registers set
55 TS = 0: TW! = 0: TK = 0: NT = 0: SS = 0: SN! = 0: SPX = 0: SPY = 0: SDX = 0: J = 0
60 DIM E(986), T(682), M$(2), MU$(12), HB(4100), HN$(10), HS!(10), HL$(10)
65 DIM TX(16), TY(16), TC(16), QX(3), QY(3), QC(3)
70 M$(1) = "MOON LANDING": M$(2) = "EXIT TO DOS"
80 GOSUB 5000
85 RESTORE 9600: READ NT: FOR I = 1 TO NT: READ TX(I), TY(I), TC(I): NEXT I: QX(1) = -1: QX(2) = -1: QX(3) = -1: SN! = TIMER + 5
100 REM ---- load art with the display switched off ----
110 SCREEN 1, 0: COLOR 0, 1: CLS
120 OUT &H3D8, &H6
130 DEF SEG = &HB800: BLOAD "MOONBG.PIC", 0: DEF SEG
140 BLOAD "EARTH.SPR", VARPTR(E(0))
150 BLOAD "TITLE.SPR", VARPTR(T(0))
170 GOSUB 8950
180 IF SK% = 1 THEN MI = NMU + 1: GOTO 400
200 REM ---- earthrise: draw only the rows above the horizon ----
210 GOSUB 900
220 T0! = TIMER
230 FOR K = 1 TO HT - EY
240 Y = HT - K
250 IF K < SH THEN E(1) = K ELSE E(1) = SH
255 PUT (EX, Y), E, PSET
260 GOSUB 900: GOSUB 950
270 IF INKEY$ <> "" THEN KP = 1: GOTO 400
280 IF TIMER < T0! + K * DT! THEN GOTO 260
290 NEXT K
400 REM ---- title; once the music ends show high scores; then the menu ----
405 GOSUB 990
410 LINE (EX, EY)-(EX + 95, HT - 1), 0, BF: E(1) = SH: PUT (EX, EY), E, PSET
420 PUT (24, 8), T, PSET
425 IF SK% <> 1 AND KP = 0 THEN GOSUB 1000
430 LINE (72, 146)-(247, 197), 0, BF: LINE (72, 146)-(247, 197), 1, B
440 LOCATE 20, 12: PRINT "- SELECT MISSION -";
450 FOR K = 1 TO NM: LOCATE 20 + 2 * K, 15: PRINT M$(K);: NEXT K
460 GOSUB 600
470 GOSUB 900: GOSUB 950: A$ = INKEY$: IF A$ = "" THEN 470
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
700 REM ---- moon landing: load the level from the LUNAR LANDING disk (drive B:, or A: when there is only one drive) ----
705 IF LD$ = "A:" THEN P$ = "INSERT THE LUNAR LANDING DISK": GOSUB 780: IF A$ = CHR$(27) THEN 470
710 ON ERROR GOTO 750: CHAIN LD$ + "LANDER"
750 RESUME 755
755 ON ERROR GOTO 0: P$ = "LUNAR LANDING DISK NOT FOUND": GOSUB 780: IF A$ = CHR$(27) THEN 470 ELSE 710
780 GET (16, 60)-(303, 107), HB: LINE (16, 60)-(303, 107), 0, BF: LINE (16, 60)-(303, 107), 2, B: LOCATE 10, 21 - LEN(P$) \ 2: PRINT P$;
782 LOCATE 12, 7: PRINT "IN DRIVE "; LD$; " AND PRESS A KEY";: LOCATE 13, 14: PRINT "(ESC = CANCEL)";
785 SOUND 200, 3: A$ = INKEY$: IF A$ <> "" THEN 785
790 GOSUB 900: A$ = INKEY$: IF A$ = "" THEN 790
795 PUT (16, 60), HB, PSET: RETURN
800 REM ---- exit ----
810 SCREEN 0, 0: WIDTH 80: SYSTEM
900 REM ---- feed music a few notes at a time so PLAY never blocks ----
910 IF MI <= NMU THEN IF PLAY(0) < 4 THEN PLAY MU$(MI): MI = MI + 1
920 RETURN
950 REM ---- life on the title: stars twinkle, now and then a shooting star streaks past ----
952 IF TIMER < TW! THEN RETURN
954 TW! = TIMER + .06: IF SS THEN GOSUB 970 ELSE IF TIMER > SN! THEN GOSUB 965
956 TK = TK + 1: IF TK MOD 4 THEN RETURN
958 IF TS THEN PSET (TX(TS), TY(TS)), TC(TS)
960 TS = INT(RND * NT) + 1: IF RND < .6 THEN PSET (TX(TS), TY(TS)), 0 ELSE TS = 0
962 RETURN
965 SS = 1: SPY = 40 + INT(RND * 20): IF RND < .5 THEN SPX = 60 + INT(RND * 30): SDX = -4 ELSE SPX = 224 + INT(RND * 30): SDX = 4
966 RETURN
970 IF QX(3) >= 0 THEN LINE (QX(3), QY(3))-(QX(3) - SDX, QY(3) - 2), 0
972 QX(3) = QX(2): QY(3) = QY(2): QX(2) = QX(1): QY(2) = QY(1): IF QX(2) >= 0 THEN LINE (QX(2), QY(2))-(QX(2) - SDX, QY(2) - 2), 1
974 IF SS > 14 THEN QX(1) = -1: IF QX(3) < 0 THEN SS = 0: SN! = TIMER + 5 + RND * 8: RETURN ELSE RETURN
976 SPX = SPX + SDX: SPY = SPY + 2: QX(1) = SPX: QY(1) = SPY: LINE (SPX, SPY)-(SPX - SDX, SPY - 2), 3: SS = SS + 1: RETURN
990 REM ---- put back any star or shooting-star pixels before the screen changes ----
992 FOR J = 3 TO 1 STEP -1: IF QX(J) >= 0 THEN LINE (QX(J), QY(J))-(QX(J) - SDX, QY(J) - 2), 0: QX(J) = -1
994 NEXT J: IF TS THEN PSET (TX(TS), TY(TS)), TC(TS): TS = 0
996 SS = 0: SN! = TIMER + 6: RETURN
1000 REM ---- attract: wait for the music to finish, show high scores ~6 s ----
1010 GOSUB 900: GOSUB 950: IF INKEY$ <> "" THEN RETURN
1020 IF MI <= NMU OR PLAY(0) > 0 THEN 1010
1030 T0! = TIMER + 1
1035 IF INKEY$ <> "" THEN RETURN ELSE IF TIMER < T0! THEN 1035
1040 GOSUB 990: GET (32, 44)-(287, 171), HB: GOSUB 8100: HR = 0: GOSUB 8500
1050 LOCATE 20, 14: PRINT "PRESS ANY KEY";: T0! = TIMER + 6
1060 IF INKEY$ = "" AND TIMER < T0! THEN 1060
1070 PUT (32, 44), HB, PSET: RETURN
5000 REM ---- Also sprach Zarathustra (opening) ----
5010 FOR K = 1 TO 9: READ MU$(K): NEXT K: NMU = 9: RETURN
5020 DATA "MBT100O1C1O3L4C2G2", "O4C2.E16E-1"
5030 DATA "O2L8CO1GO2CO1G", "O2CO1GO2CO1GO2C4"
5040 DATA "O3L4C2G2O4C2.E-16E1"
5050 DATA "O2L8CO1GO2CO1G", "O2CO1GO2CO1GO2C4"
5060 DATA "O3L4C2G2O4C2.", "A1B4O5C1."
8100 REM ---- load the high score table (empty until the first scores are saved in LANDHS.DAT) ----
8110 HE = 0: ON ERROR GOTO 8180
8120 OPEN "LANDHS.DAT" FOR INPUT AS #1
8130 IF HE = 0 THEN FOR I = 1 TO 10: INPUT #1, HN$(I), HS!(I), HL$(I): NEXT I
8140 CLOSE #1: ON ERROR GOTO 0
8150 IF HE THEN FOR I = 1 TO 10: HN$(I) = "": HS!(I) = 0: HL$(I) = "": NEXT I
8160 RETURN
8180 HE = 1: RESUME NEXT
8500 REM ---- draw the high score table; HR = rank to highlight (0 = none) ----
8510 LINE (32, 44)-(287, 171), 0, BF: LINE (32, 44)-(287, 171), 1, B
8520 LOCATE 7, 15: PRINT "HIGH SCORES";: LINE (116, 57)-(203, 57), 1
8530 FOR I = 1 TO 10: LOCATE 8 + I, 7: IF HS!(I) > 0 THEN PRINT USING "##. \ \  ######  "; I; HN$(I); HS!(I);: PRINT HL$(I); ELSE PRINT USING "##.  ---"; I;
8535 NEXT I
8540 IF HR THEN LINE (44, 55 + 8 * HR)-(277, 64 + 8 * HR), 2, B
8550 RETURN
8940 REM ---- display on, palette cyan / red / grey (CGA: the mode register's B/W bit). A Tandy 1000 picks palette registers 3, 4, 7 for that, so open its palette mask (it masks them to 0-3) and set them ----
8950 OUT &H3D8, &HE: OUT &H3D9, 0: IF TY = 0 THEN RETURN
8952 I = INP(&H3DA): OUT &H3DA, 1: OUT &H3DE, &HF: OUT &H3DA, &H10: OUT &H3DE, 0: OUT &H3DA, &H13: OUT &H3DE, 3: OUT &H3DA, &H14: OUT &H3DE, 4: OUT &H3DA, &H17: OUT &H3DE, 7: RETURN
9590 REM ---- stars that twinkle: count, then x, y, colour (picked by tools/mkstars.py from MOONBG.PIC) ----
9600 DATA 16,10,73,3,11,81,3,28,109,3,30,58,3,44,58,3,52,70,1,71,98,3,93,119
9601 DATA 3,242,58,3,242,118,3,248,40,1,274,92,3,281,42,3,303,82,1,306,99,3,317,53
9602 DATA 3
