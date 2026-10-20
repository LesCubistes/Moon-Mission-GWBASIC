10 REM ==== MOON LANDING - phase 1: pick a site from orbit; phase 2: land the lunar module ====
20 REM Runs from the LUNAR LANDING disk (drive LD$, normally B:). Started by MOON on the START disk.
25 REM Keypad: 8/5 throttle up/down, 0 or SPACE engine off, 7 9 4 6 1 2 3 thrusters
30 COMMON SK%, LS%, LD$
40 DEFINT A-Z: KEY OFF: RANDOMIZE TIMER
50 REM -- every simple variable is created here, before any VARPTR/BLOAD --
60 X! = 0: Y! = 0: VX! = 0: VY! = 0: F! = 0: A! = 0: DT! = 0: T0! = 0: T1! = 0: ST! = 0
70 HT! = 0: PT! = 0: TT! = 0: GR! = 3: AM! = 7: DV! = .8: VYS! = 4: VXS! = 2
80 FM! = 800: BU! = 25: RF! = 4
90 XI = 0: YI = 0: OX = -1: OY = 0: FL = 0: OF = 0: PF = 0: OP = 0: TH = 0: K = 0: I = 0
100 LK = 0: B = 0: P = 0: NP = 0: LV = 1: S = 1: SC = 0: W = 0: AL = 0: LF = 0: RG = 0: MN = 0: Q = 0
105 CT = 0: D = 0: CX = 0: GC = 0: PX = 0: PY = 0: PO = 0: PZ = 0: R = 0: J = 0: Z = 0
107 FX = 0: FY = 0: FR = 0: GX = 0: GY = 0: DW = 0: ALM = 0: WD! = 0: T2! = 0: AT! = 0: RL! = 0: LN = 0: SF = 0: TB = 0: LP = 0: HR = 0
108 HE = 0: LT! = 0: TS! = 0: BX! = 0: BV! = 0: BI = 0: BO = -1: BY = 0: ZN = 0: OZ = 0: MT! = 0: IM = 0: DU = 0: DX = 0: DY = 0: DC = 0
110 K$ = "": C$ = "": R$ = "": R2$ = "": M$ = "": N$ = "": PC$ = "": MP$ = ""
112 LD$ = LD$ + "": REM "" when run on its own: assets then come from the current drive
120 DIM H(639), SP(146), MK(146), BG(146), F1(146), F2(146), F3(146)
125 DIM Q1(146), Q2(146), Q3(146), Q4(146), Q6(146), Q7(146), Q9(146)
127 DIM B2(172), FB(450), C1(172), C2(172), C3(172), C4(172), C5(172), C6(172), C7(172)
128 DIM M1(172), M2(172), M3(172), M4(172), M5(172), M6(172), M7(172), EU(6), EV(6)
130 DIM LA(4), LB(4), LM(4), RX!(9), RY!(9), SN$(3), SD$(3), SA(3), HN$(10), HS!(10), HL$(10), ZX(3), ZY(3), ZW(3), ZH(3)
131 DIM D1(115), D2(115), D3(115), D4(115), D5(115), D6(115)
140 FOR I = 1 TO 9: READ RX!(I), RY!(I): NEXT I
150 FOR I = 1 TO 3: READ SN$(I), SD$(I), SA(I): NEXT I
155 FOR I = 1 TO 6: READ EU(I), EV(I): NEXT I
157 FOR I = 1 TO 3: READ ZX(I), ZY(I), ZW(I), ZH(I): NEXT I
160 BLOAD LD$ + "LMSHIP.SPR", VARPTR(SP(0))
170 BLOAD LD$ + "LMMASK.SPR", VARPTR(MK(0))
180 BLOAD LD$ + "FL1.SPR", VARPTR(F1(0)): BLOAD LD$ + "FL2.SPR", VARPTR(F2(0)): BLOAD LD$ + "FL3.SPR", VARPTR(F3(0))
182 BLOAD LD$ + "RC1.SPR", VARPTR(Q1(0)): BLOAD LD$ + "RC2.SPR", VARPTR(Q2(0)): BLOAD LD$ + "RC3.SPR", VARPTR(Q3(0))
184 BLOAD LD$ + "RC4.SPR", VARPTR(Q4(0)): BLOAD LD$ + "RC6.SPR", VARPTR(Q6(0))
186 BLOAD LD$ + "RC7.SPR", VARPTR(Q7(0)): BLOAD LD$ + "RC9.SPR", VARPTR(Q9(0))
187 BLOAD LD$ + "CP1.SPR", VARPTR(C1(0)): BLOAD LD$ + "CP2.SPR", VARPTR(C2(0)): BLOAD LD$ + "CP3.SPR", VARPTR(C3(0))
188 BLOAD LD$ + "CP4.SPR", VARPTR(C4(0)): BLOAD LD$ + "CP5.SPR", VARPTR(C5(0)): BLOAD LD$ + "CP6.SPR", VARPTR(C6(0))
189 BLOAD LD$ + "CP7.SPR", VARPTR(C7(0)): BLOAD LD$ + "CM1.SPR", VARPTR(M1(0)): BLOAD LD$ + "CM2.SPR", VARPTR(M2(0))
191 BLOAD LD$ + "CM3.SPR", VARPTR(M3(0)): BLOAD LD$ + "CM4.SPR", VARPTR(M4(0)): BLOAD LD$ + "CM5.SPR", VARPTR(M5(0))
192 BLOAD LD$ + "CM6.SPR", VARPTR(M6(0)): BLOAD LD$ + "CM7.SPR", VARPTR(M7(0))
194 BLOAD LD$ + "DU1.SPR", VARPTR(D1(0)): BLOAD LD$ + "DU2.SPR", VARPTR(D2(0)): BLOAD LD$ + "DU3.SPR", VARPTR(D3(0))
195 SCREEN 1, 0: COLOR 0, 1: PLAY "MB"
196 BLOAD LD$ + "DU4.SPR", VARPTR(D4(0)): BLOAD LD$ + "DU5.SPR", VARPTR(D5(0)): BLOAD LD$ + "DU6.SPR", VARPTR(D6(0))
200 REM ==== phase 1: orbit - drift left/right, then burn down to a site (no fuel, no points) ====
210 OUT &H3D8, &H6: CLS
220 DEF SEG = &HB800: BLOAD LD$ + "ORBIT.PIC", 0: DEF SEG
230 BX! = 146: BV! = 0: BY = 48: OX = -1: OZ = 0: OP = -1: PF = 0: FL = 0: MT! = 0: T0! = TIMER
240 OUT &H3D8, &HE: OUT &H3D9, 0
250 T1! = TIMER: DT! = T1! - T0!: IF DT! < .05 AND DT! >= 0 THEN 250
255 IF DT! > .3 OR DT! < 0 THEN DT! = .3
260 T0! = T1!
265 K$ = INKEY$: IF K$ = "" THEN 300
270 IF K$ = CHR$(0) + "K" OR K$ = "4" OR K$ = "7" OR K$ = "1" THEN BV! = BV! - 10: PF = 4: PT! = T1! + .2
275 IF K$ = CHR$(0) + "M" OR K$ = "6" OR K$ = "9" OR K$ = "3" THEN BV! = BV! + 10: PF = 6: PT! = T1! + .2
280 IF K$ = CHR$(0) + "P" OR K$ = "2" OR K$ = CHR$(13) THEN 400
285 IF K$ = CHR$(27) THEN SK% = 1: ON ERROR GOTO 8800: CHAIN "MOON"
290 GOTO 265
300 IF BV! > 60 THEN BV! = 60 ELSE IF BV! < -60 THEN BV! = -60
305 BV! = BV! * (1 - .6 * DT!): BX! = BX! + BV! * DT!
310 IF BX! < 4 THEN BX! = 4: BV! = 0 ELSE IF BX! > 288 THEN BX! = 288: BV! = 0
315 BI = INT(BX!): ZN = (BI + 14) \ 107 + 1: IF ZN > 3 THEN ZN = 3
320 IF T1! > PT! THEN PF = 0
325 IF ZN <> OZ THEN GOSUB 380
330 IF BI <> OX OR PF <> OP THEN XI = BI: YI = BY: GOSUB 5000
335 IF MT! > 0 THEN IF T1! > MT! THEN LINE (0, 16)-(319, 23), 0, BF: MT! = 0
340 GOTO 250
380 REM ---- highlight the zone under the lander ----
382 IF OZ THEN LINE (ZX(OZ), ZY(OZ))-(ZW(OZ), ZH(OZ)), 0, B
384 LINE (ZX(ZN), ZY(ZN))-(ZW(ZN), ZH(ZN)), 2, B: OZ = ZN: SOUND 500, 1: RETURN
400 REM ---- descent: the up-facing thrusters push the lander down toward the site ----
405 IF SA(ZN) = 0 THEN M$ = SN$(ZN) + " - COMING SOON": LINE (0, 16)-(319, 23), 0, BF: LOCATE 3, 21 - LEN(M$) \ 2: PRINT M$;: SOUND 150, 4: MT! = T1! + 2.5: GOTO 265
410 LV = ZN: LS% = ZN: LN = 1: PLAY "T200O3L32CDEFGAB"
415 PF = 2: FOR J = 1 TO 6: XI = BI: YI = BY + 2 * J: GOSUB 5000
430 SOUND 120 - J * 8, 1: WD! = .1: GOSUB 7900: NEXT J
435 WD! = .4: GOSUB 7900
440 IF INKEY$ <> "" THEN 440
445 GOTO 1000
1000 REM ==== load and start the level ====
1010 OUT &H3D8, &H6: CLS
1015 ON LV GOSUB 8700, 8710, 8720: READ PC$, MP$, X!, Y!, VX!, VY!, FM!, NP: FOR I = 1 TO NP: READ LA(I), LB(I), LM(I): NEXT I
1020 DEF SEG = &HB800: BLOAD LD$ + PC$, 0: DEF SEG
1030 BLOAD LD$ + MP$, VARPTR(H(0))
1050 F! = FM!: TH = 0: PF = 0: OX = -1: OF = -1: OP = -1
1060 OUT &H3D8, &HE: OUT &H3D9, 0
1070 LOCATE 1, 17: PRINT USING "LANDER #/3"; LN;
1080 LOCATE 4, 21 - LEN(SN$(LV)) \ 2: PRINT SN$(LV);
1090 T0! = TIMER: ST! = T0!: TT! = T0! + 3: HT! = 0
2000 REM ==== main loop ====
2010 T1! = TIMER: DT! = T1! - T0!: IF DT! < .05 AND DT! >= 0 THEN 2010
2020 IF DT! > .3 OR DT! < 0 THEN DT! = .3
2030 T0! = T1!: LK = 0
2040 K$ = INKEY$: IF K$ = "" THEN 2100
2050 GOSUB 3000: IF Q THEN 200
2060 GOTO 2040
2100 A! = GR!
2110 IF TH > 0 THEN A! = GR! - AM! * TH / 10: F! = F! - BU! * TH / 10 * DT!: IF F! <= 0 THEN F! = 0: TH = 0
2120 VY! = VY! + A! * DT!: X! = X! + VX! * DT!: Y! = Y! + VY! * DT!
2130 IF X! < 4 THEN X! = 4: VX! = 0
2140 IF X! > 288 THEN X! = 288: VX! = 0
2150 IF Y! < 21 THEN Y! = 21: IF VY! < 0 THEN VY! = 0
2160 XI = INT(X!): YI = INT(Y!)
2170 IF YI + 22 >= H(320 + XI) THEN 4000
2180 FL = -(TH > 0) - (TH > 3) - (TH > 7)
2190 IF T1! > PT! THEN PF = 0
2195 IF DU THEN GOSUB 2300
2200 IF XI <> OX OR YI <> OY OR FL <> OF OR PF <> OP THEN GOSUB 5000
2205 Z = H(XI + 14) - YI - 22: IF TH > 2 AND Z < 30 THEN GOSUB 2320
2210 IF T1! >= HT! THEN GOSUB 6000: HT! = T1! + .25
2220 IF TT! > 0 THEN IF T1! > TT! THEN LINE (96, 24)-(231, 31), 0, BF: TT! = 0
2230 GOTO 2010
2300 REM ---- engine dust: erase last frame's plume (XOR again restores the ground exactly) ----
2305 ON DU GOSUB 2311, 2312, 2313, 2314, 2315, 2316: DU = 0: RETURN
2311 PUT (DX, DY), D1, XOR: RETURN
2312 PUT (DX, DY), D2, XOR: RETURN
2313 PUT (DX, DY), D3, XOR: RETURN
2314 PUT (DX, DY), D4, XOR: RETURN
2315 PUT (DX, DY), D5, XOR: RETURN
2316 PUT (DX, DY), D6, XOR: RETURN
2320 REM ---- engine dust: bigger plume the lower we are, two shimmer variants ----
2325 DU = 1 - 2 * (Z < 20) - 2 * (Z < 10) + (DC AND 1): DC = DC + 1
2330 DX = XI - 22: IF DX < 0 THEN DX = 0 ELSE IF DX > 248 THEN DX = 248
2335 DY = H(XI + 14) - 12: ON DU GOSUB 2311, 2312, 2313, 2314, 2315, 2316: RETURN
3000 REM ---- one key ----
3010 Q = 0: K = 0
3020 IF LEN(K$) = 2 THEN K = INSTR("OPQKLMGHI", RIGHT$(K$, 1)): GOTO 3060
3030 IF K$ = CHR$(27) THEN Q = 1: RETURN
3040 IF K$ = "0" OR K$ = " " THEN TH = 0: RETURN
3050 IF K$ = "-" THEN K = 5 ELSE IF K$ = "+" THEN K = 8 ELSE K = INSTR("123456789", K$)
3060 IF K = 0 OR K = LK THEN RETURN
3065 LK = K
3070 IF K = 8 THEN TH = TH - (TH < 10 AND F! > 0): RETURN
3080 IF K = 5 THEN TH = TH + (TH > 0): RETURN
3090 IF F! < RF! THEN RETURN
3100 F! = F! - RF!: VX! = VX! + RX!(K) * DV!: VY! = VY! + RY!(K) * DV!
3110 PF = K: PT! = T1! + .2: RETURN
4000 REM ---- touchdown: which outcome? ----
4005 IF DU THEN GOSUB 2300
4010 LF = H(XI + 1): RG = H(XI + 26): MN = H(320 + XI)
4020 P = 0: FOR I = 1 TO NP: IF XI + 1 > LA(I) AND XI + 26 < LB(I) THEN P = I
4030 NEXT I
4040 CT = 0: R$ = "": R2$ = "": D = SGN(VX!): IF D = 0 THEN D = 1
4050 IF ABS(VX!) > VXS! THEN CT = 3: IF ABS(VX!) > 3 AND F! > FM! * .25 AND RND < .2 THEN CT = 5
4060 IF CT = 0 AND (LF <> MN OR RG <> MN) THEN CT = 4
4070 IF CT = 0 AND VY! > VYS! THEN CT = 1
4080 IF VY! > 7 AND CT <> 5 THEN CT = 2
4085 IF TT! > 0 THEN LINE (96, 24)-(231, 31), 0, BF: TT! = 0
4090 YI = MN - 22: TH = 0: FL = 0: PF = 0: GOSUB 5000: GOSUB 6000
4100 CX = XI + 14: GC = H(CX): PO = 0
4110 IF CT THEN ON CT GOSUB 7100, 7200, 7300, 7400, 7500: GOTO 4400
4200 REM ==== landed: (soft landing + time bonus) x pad x lander ====
4205 IF P THEN W = LM(P) ELSE W = 1
4210 LT! = T1! - ST!: SF = 500 - INT(125 * VY! + 100 * ABS(VX!)): IF SF < 0 THEN SF = 0
4215 TB = 2000 - INT(50 * LT!): IF TB < 0 THEN TB = 0
4220 LP = 100: IF LN = 2 THEN LP = 50 ELSE IF LN = 3 THEN LP = 25
4225 TS! = INT(CSNG(SF + TB) * W * LP / 1000 + .5) * 10
4230 PLAY "T160O4L16CEG>C8": WD! = 1: GOSUB 7900: PC$ = "LANDED.PIC": GOSUB 4600
4235 LOCATE 1, 11: PRINT "THE EAGLE HAS LANDED";: LOCATE 2, 21 - LEN(SN$(LV)) \ 2: PRINT SN$(LV);
4240 WD! = .7: GOSUB 7900: WD! = .35
4245 LOCATE 4, 2: PRINT USING "SOFT LANDING #####"; SF;: GOSUB 4295
4250 LOCATE 4, 22: PRINT USING "TIME BONUS #####"; TB;: GOSUB 4295
4255 LOCATE 5, 3: PRINT USING "LANDING PAD X##"; W;: GOSUB 4295
4260 LOCATE 5, 22: PRINT USING "LANDER # OF 3 ###_%"; LN; LP;: GOSUB 4295
4265 LOCATE 6, 15: PRINT USING "SCORE ######"; TS!;: PLAY "T200O5L16CEG>C8"
4270 LOCATE 7, 15: PRINT "PRESS ENTER";
4275 IF INKEY$ <> "" THEN 4275
4280 K$ = INKEY$: IF K$ <> CHR$(13) THEN 4280
4285 GOTO 8000
4295 SOUND 700, 1: GOSUB 7900: RETURN
4400 REM ==== crashed: with landers left, a quick box and the next lander; the last one ends the level ====
4402 IF LN = 3 THEN 4470
4405 LINE (64, 60)-(255, 107), 0, BF: LINE (64, 60)-(255, 107), 2, B
4410 LOCATE 9, 21 - LEN(R$) \ 2: PRINT R$;
4415 LOCATE 10, 21 - LEN(R2$) \ 2: PRINT R2$;
4420 LOCATE 12, 14: PRINT USING "LANDERS LEFT #"; 3 - LN;: LOCATE 13, 10: PRINT "ENTER=NEXT  ESC=ORBIT";
4425 GOTO 4430
4430 IF INKEY$ <> "" THEN 4430
4440 K$ = INKEY$: IF K$ = "" THEN 4440
4445 IF K$ = CHR$(27) THEN 200
4450 IF K$ <> CHR$(13) THEN 4440
4455 IF LN < 3 THEN LN = LN + 1: GOTO 1000
4460 GOTO 200
4470 REM ---- end of level, all three landers lost: the wreck, or the crater if the last one blew up ----
4472 WD! = .8: GOSUB 7900: PC$ = "WRECK.PIC": IF CT = 2 OR CT = 5 THEN PC$ = "CRATER.PIC"
4474 GOSUB 4600: LOCATE 1, 21 - LEN(R$) \ 2: PRINT R$;: LOCATE 2, 21 - LEN(R2$) \ 2: PRINT R2$;
4476 LOCATE 3, 21 - LEN(SN$(LV)) \ 2: PRINT SN$(LV);: LOCATE 4, 14: PRINT "MISSION FAILED";
4478 LOCATE 5, 15: PRINT "PRESS ENTER";: PLAY "T90O2L4GE-C2"
4479 GOTO 4430
4600 REM ---- end-of-level picture PC$ (LANDED, WRECK or CRATER), loaded with the display off ----
4610 OUT &H3D8, &H6: DEF SEG = &HB800: BLOAD LD$ + PC$, 0: DEF SEG: OUT &H3D8, &HE: RETURN
5000 REM ---- draw lander: restore old background, save new, mask, ship, effects ----
5010 IF OX >= 0 THEN PUT (OX - 4, OY - 3), BG, PSET
5020 GET (XI - 4, YI - 3)-(XI + 31, YI + 28), BG
5030 PUT (XI - 4, YI - 3), MK, AND: PUT (XI - 4, YI - 3), SP, OR
5040 ON FL GOSUB 5110, 5120, 5130
5050 ON PF GOSUB 5141, 5142, 5143, 5144, 5199, 5146, 5147, 5199, 5149
5060 OX = XI: OY = YI: OF = FL: OP = PF: RETURN
5110 PUT (XI - 4, YI - 3), F1, OR: RETURN
5120 PUT (XI - 4, YI - 3), F2, OR: RETURN
5130 PUT (XI - 4, YI - 3), F3, OR: RETURN
5141 PUT (XI - 4, YI - 3), Q1, OR: RETURN
5142 PUT (XI - 4, YI - 3), Q2, OR: RETURN
5143 PUT (XI - 4, YI - 3), Q3, OR: RETURN
5144 PUT (XI - 4, YI - 3), Q4, OR: RETURN
5146 PUT (XI - 4, YI - 3), Q6, OR: RETURN
5147 PUT (XI - 4, YI - 3), Q7, OR: RETURN
5149 PUT (XI - 4, YI - 3), Q9, OR: RETURN
5199 RETURN
6000 REM ---- HUD ----
6010 W = INT(F! / FM! * 78)
6020 IF W > 0 THEN LINE (42, 2)-(41 + W, 4), 1, BF
6030 IF W < 78 THEN LINE (42 + W, 2)-(119, 4), 0, BF
6040 AL = (H(XI + 14) - YI - 22) * 5: IF AL < 0 THEN AL = 0
6050 LOCATE 2, 1: PRINT USING "ALT #### H+##.# V+##.# THR ###"; AL; VX!; -VY!; TH * 10;
6060 I = INT(T1! - ST!): LOCATE 1, 32: PRINT USING "T ##"; I \ 60;: PRINT ":"; RIGHT$(STR$(100 + I MOD 60), 2);
6070 RETURN
7000 REM ---- draw crash pose PZ centred on column CX, resting on ground row GC ----
7010 IF PO THEN PUT (PX, PY), B2, PSET ELSE IF OX >= 0 THEN PUT (OX - 4, OY - 3), BG, PSET: OX = -1
7020 PX = CX - 20: IF PX < 0 THEN PX = 0 ELSE IF PX > 280 THEN PX = 280
7030 PY = GC - 34: IF PY > 165 THEN PY = 165
7040 GET (PX, PY)-(PX + 39, PY + 33), B2: PO = 1
7050 ON PZ GOSUB 7061, 7062, 7063, 7064, 7065, 7066, 7067
7060 RETURN
7061 PUT (PX, PY), M1, AND: PUT (PX, PY), C1, OR: RETURN
7062 PUT (PX, PY), M2, AND: PUT (PX, PY), C2, OR: RETURN
7063 PUT (PX, PY), M3, AND: PUT (PX, PY), C3, OR: RETURN
7064 PUT (PX, PY), M4, AND: PUT (PX, PY), C4, OR: RETURN
7065 PUT (PX, PY), M5, AND: PUT (PX, PY), C5, OR: RETURN
7066 PUT (PX, PY), M6, AND: PUT (PX, PY), C6, OR: RETURN
7067 PUT (PX, PY), M7, AND: PUT (PX, PY), C7, OR: RETURN
7100 REM ---- 1 hard landing: legs fold, lander slumps ----
7110 DW = 18: GOSUB 7800: SOUND 70, 2
7120 PZ = 1: GOSUB 7000: DW = 24: GOSUB 7800: GOSUB 7850: WD! = .4: GOSUB 7900
7130 PZ = 2: GOSUB 7000: GOSUB 7850: SOUND 50, 3: WD! = .6: GOSUB 7900
7140 FOR J = 1 TO 6: PSET (CX + 6 + RND * 8, PY + 10 - RND * 10), 3: NEXT J
7150 R$ = "HARD LANDING": R2$ = "LANDING LEGS COLLAPSED": RETURN
7200 REM ---- 2 impact: fireball, debris, crater (PAINT is fast machine code) ----
7205 IF FR = 0 THEN FR = 18
7210 IF OX >= 0 THEN PUT (OX - 4, OY - 3), BG, PSET: OX = -1
7212 IF PO THEN PUT (PX, PY), B2, PSET: PO = 0
7214 FX = CX: FY = GC: GOSUB 7950: SOUND 40, 2
7220 FOR R = 6 TO FR STEP 6: CIRCLE (FX, FY - 8), R, 2: PAINT (FX, FY - 8), 2, 2
7225 CIRCLE (FX, FY - 8), R \ 3, 3: PAINT (FX, FY - 8), 3, 3: SOUND 37 + RND * 60, 1: NEXT R
7230 FOR Z = 1 TO 6: FOR J = 1 TO 6
7235 PSET (FX + EU(J) * Z, FY - 8 - EV(J) * Z + Z * Z), 3 - (J AND 1)
7240 NEXT J: NEXT Z
7245 WD! = .25: GOSUB 7900
7250 PUT (GX, GY), FB, PSET: CIRCLE (FX, FY - 8), FR, 2: CIRCLE (FX, FY - 8), FR - 3, 2: WD! = .2: GOSUB 7900
7255 PUT (GX, GY), FB, PSET: CIRCLE (FX, FY - 8), FR + 4, 2: WD! = .15: GOSUB 7900
7260 PUT (GX, GY), FB, PSET
7275 FOR J = -16 TO 16: I = FX + J: IF I >= 0 AND I < 320 THEN Z = INT(4 * (1 - (J / 16) ^ 2)): LINE (I, H(I) - 1)-(I, H(I) + Z), 0
7280 NEXT J
7285 FOR J = 0 TO 7: I = FX + INT(RND * 40) - 20: IF I >= 0 AND I < 319 THEN PSET (I, H(I) - 2), 2 + (J MOD 2)
7290 NEXT J
7295 IF R$ = "" THEN R$ = "IMPACT": R2$ = "LANDER DESTROYED"
7298 FR = 0: RETURN
7300 REM ---- 3 sideways: a foot catches, tips over and rolls ----
7310 SOUND 90, 1: PZ = 4 + (D > 0): CX = CX + 3 * D: GOSUB 7000: DW = 16: GOSUB 7800: WD! = .3: GOSUB 7900
7320 PZ = 6 + (D > 0): CX = CX + 6 * D: GC = H(CX): GOSUB 7000: GOSUB 7800: GOSUB 7850: SOUND 60, 3: WD! = .5: GOSUB 7900
7330 FOR J = 1 TO 3: PSET (PX + 20 - 12 * D, PY + 14), 1: WD! = .3: GOSUB 7900: PSET (PX + 20 - 12 * D, PY + 14), 0: GOSUB 7900: NEXT J
7340 R$ = "TIPPED OVER": R2$ = "DRIFTING SIDEWAYS": RETURN
7400 REM ---- 4 steep ground: slides downhill and flips ----
7405 D = SGN(RG - LF): IF D = 0 THEN D = 1
7410 PZ = 4 + (D > 0): CX = CX + 4 * D: GC = H(CX): GOSUB 7000: DW = 12: GOSUB 7800: WD! = .35: GOSUB 7900
7420 CX = CX + 6 * D: GC = H(CX): GOSUB 7000: GOSUB 7800: WD! = .3: GOSUB 7900
7430 PZ = 7: CX = CX + 6 * D: GC = H(CX): GOSUB 7000: DW = 18: GOSUB 7800: SOUND 55, 3: WD! = .6: GOSUB 7900
7440 R$ = "SLID OFF THE RIM": R2$ = "GROUND TOO STEEP": RETURN
7500 REM ---- 5 rare: impact jams the main engine on and a side thruster firing ----
7510 R$ = "MAYDAY": R2$ = "THRUSTER MALFUNCTION": GOSUB 7850: SOUND 100, 1
7520 VY! = -2: VX! = VX! + 2 * D: Y! = YI - 1: X! = XI: T0! = TIMER: AT! = 0: ALM = 0: RL! = F! / 1.5: IF RL! < 100 THEN RL! = 100
7540 T1! = TIMER: DT! = T1! - T0!: IF DT! < .05 AND DT! >= 0 THEN 7540
7550 IF DT! > .5 OR DT! < 0 THEN DT! = .5
7560 T0! = T1!: K$ = INKEY$
7570 A! = GR!: IF F! > 0 THEN A! = GR! - AM! * .6: F! = F! - RL! * DT!: IF F! < 0 THEN F! = 0
7580 VX! = VX! + 3 * D * DT!: VY! = VY! + A! * DT!: X! = X! + VX! * DT!: Y! = Y! + VY! * DT!
7590 IF X! < 4 THEN X! = 4: VX! = 0
7600 IF X! > 288 THEN X! = 288: VX! = 0
7610 IF Y! < 21 THEN Y! = 21: IF VY! < 0 THEN VY! = 0
7620 XI = INT(X!): YI = INT(Y!)
7630 IF YI + 22 >= H(320 + XI) THEN 7690
7640 FL = 3 * -(F! > 0): PF = 6 + 2 * (D < 0)
7650 GOSUB 5000: PSET (XI + 14 - 23 * D, YI + 14), 3: PSET (XI + 15 - 23 * D, YI + 13), 3
7660 IF T1! > AT! THEN AT! = T1! + .3: ALM = 1 - ALM: GOSUB 7700
7670 IF T1! >= HT! THEN GOSUB 6000: HT! = T1! + .25
7680 GOTO 7540
7690 YI = H(320 + XI) - 22: FL = 0: PF = 0: GOSUB 5000: LINE (110, 22)-(209, 33), 0, BF
7695 CX = XI + 14: GC = H(CX): FR = 24: GOSUB 7200: RETURN
7700 IF ALM THEN LINE (110, 22)-(209, 33), 2, B: LOCATE 4, 15: PRINT "MASTER ALARM";: SOUND 880, 1 ELSE LINE (110, 22)-(209, 33), 0, BF: SOUND 660, 1
7710 RETURN
7800 REM ---- dust kicked up around CX, half-width DW ----
7810 FOR J = 1 TO 14: Z = CX + INT(RND * 2 * DW) - DW
7820 IF Z >= 0 AND Z < 320 THEN PSET (Z, H(Z) - 1 - INT(RND * 3)), 3
7830 NEXT J: RETURN
7850 REM ---- sparks ----
7860 FOR J = 1 TO 8: PSET (CX + RND * 24 - 12, GC - 2 - RND * 14), 2: NEXT J: RETURN
7900 REM ---- wait WD! seconds ----
7910 T2! = TIMER + WD!
7920 IF TIMER < T2! THEN 7920
7930 RETURN
7950 REM ---- save the 64x56 area around the crash before the fireball ----
7960 GX = FX - 32: IF GX < 0 THEN GX = 0 ELSE IF GX > 256 THEN GX = 256
7970 GY = FY - 38: IF GY < 18 THEN GY = 18 ELSE IF GY > 144 THEN GY = 144
7980 GET (GX, GY)-(GX + 63, GY + 55), FB: RETURN
8000 REM ==== mission complete: high score check, initials, save, show table ====
8010 GOSUB 8100: HR = 0
8020 IF TS! > HS!(10) THEN GOSUB 8400
8030 GOSUB 8500: LOCATE 20, 14: PRINT "PRESS ANY KEY";
8035 IF HR > 0 AND HE THEN LOCATE 21, 12: PRINT "(DISK ERROR: NOT SAVED)";
8040 IF INKEY$ = "" THEN 8040
8050 GOTO 200
8100 REM ---- load the high score table (defaults if HISCORE.DAT is missing) ----
8110 HE = 0: ON ERROR GOTO 8180
8120 OPEN "HISCORE.DAT" FOR INPUT AS #1
8130 IF HE = 0 THEN FOR I = 1 TO 10: INPUT #1, HN$(I), HS!(I), HL$(I): NEXT I
8140 CLOSE #1: ON ERROR GOTO 0
8150 IF HE THEN RESTORE 9200: FOR I = 1 TO 10: READ HN$(I), HS!(I), HL$(I): NEXT I
8160 RETURN
8180 HE = 1: RESUME NEXT
8300 REM ---- save the table ----
8310 HE = 0: ON ERROR GOTO 8180
8320 OPEN "HISCORE.DAT" FOR OUTPUT AS #1
8330 IF HE = 0 THEN FOR I = 1 TO 10: WRITE #1, HN$(I), HS!(I), HL$(I): NEXT I
8340 CLOSE #1: ON ERROR GOTO 0: RETURN
8400 REM ---- new high score: find the rank, type initials, insert, save ----
8410 HR = 10
8415 IF HR > 1 THEN IF TS! > HS!(HR - 1) THEN HR = HR - 1: GOTO 8415
8420 LINE (56, 52)-(263, 139), 0, BF: LINE (64, 60)-(255, 123), 1, B
8425 PLAY "T180O4L16CDEFGAB>C8"
8430 LOCATE 9, 13: PRINT "NEW HIGH SCORE!";
8435 LOCATE 10, 13: PRINT USING "RANK ##  ######"; HR; TS!;
8440 LOCATE 12, 12: PRINT "TYPE YOUR INITIALS";
8445 N$ = ""
8450 LOCATE 14, 19: PRINT LEFT$(N$ + "___", 3);
8455 K$ = INKEY$: IF K$ = "" THEN 8455
8460 IF K$ >= "a" AND K$ <= "z" THEN K$ = CHR$(ASC(K$) - 32)
8465 IF LEN(K$) = 1 AND LEN(N$) < 3 AND ((K$ >= "A" AND K$ <= "Z") OR (K$ >= "0" AND K$ <= "9")) THEN N$ = N$ + K$: SOUND 800, 1
8470 IF K$ = CHR$(8) AND LEN(N$) > 0 THEN N$ = LEFT$(N$, LEN(N$) - 1)
8475 IF K$ <> CHR$(13) OR N$ = "" THEN 8450
8480 IF HR < 10 THEN FOR I = 10 TO HR + 1 STEP -1: HN$(I) = HN$(I - 1): HS!(I) = HS!(I - 1): HL$(I) = HL$(I - 1): NEXT I
8485 HN$(HR) = N$: HS!(HR) = TS!: HL$(HR) = LEFT$(SN$(LV), 12)
8490 GOSUB 8300: RETURN
8500 REM ---- draw the high score table; HR = rank to highlight (0 = none) ----
8510 LINE (32, 44)-(287, 171), 0, BF: LINE (32, 44)-(287, 171), 1, B
8520 LOCATE 7, 15: PRINT "HIGH SCORES";: LINE (116, 57)-(203, 57), 1
8530 FOR I = 1 TO 10: LOCATE 8 + I, 7: PRINT USING "##. \ \  ######  "; I; HN$(I); HS!(I);: PRINT HL$(I);: NEXT I
8540 IF HR THEN LINE (44, 55 + 8 * HR)-(277, 64 + 8 * HR), 2, B
8550 RETURN
8690 REM ---- point READ at the chosen site's level data ----
8700 RESTORE 9110: RETURN
8710 RESTORE 9130: RETURN
8720 RESTORE 9150: RETURN
8800 RESUME 8810: REM MOON is not on this disk (level run on its own): back to DOS
8810 SCREEN 0, 0: WIDTH 80: SYSTEM
9000 REM ---- thrusters: push x, push y for keys 1-9 (5 and 8 are throttle) ----
9010 DATA -.707,.707, 0,1, .707,.707, -1,0, 0,0, 1,0, -.707,-.707, 0,0, .707,-.707
9055 REM ---- landing sites: name, description, available? ----
9060 DATA "TRANQUILITY BASE", "APOLLO 11 - EASY", 1
9070 DATA "FRA MAURO", "APOLLO 14 - MEDIUM", 1
9080 DATA "HADLEY RILLE", "APOLLO 15 - HARD", 1
9090 REM ---- debris directions for the explosion (x step, upward step) ----
9095 DATA -5,6, -3,8, -1,9, 2,9, 4,7, 5,5
9096 REM ---- phase 1 zone highlight boxes (x0, y0, x1, y1), matching ORBIT.PIC ----
9097 DATA 5,93,97,113, 117,85,193,105, 213,93,313,113
9100 REM ---- levels: picture, map, start x, y, x speed, y speed, fuel, pads (left x, right x, multiplier) ----
9110 DATA "EASY.PIC", "EASY.MAP", 40, 24, 6, 1, 800, 3, 12,68,2, 140,184,3, 256,292,5
9120 REM Fra Mauro: rolling hills, a ridge to climb, boulders, Cone crater
9130 DATA "MEDIUM.PIC", "MEDIUM.MAP", 40, 24, 8, 1, 700, 3, 18,64,3, 150,190,5, 270,304,7
9140 REM Hadley Rille: Mount Hadley, the x7 pad down in the rille, the x10 mesa by Hadley Delta
9150 DATA "HARD.PIC", "HARD.MAP", 20, 24, 10, 1, 650, 3, 8,48,4, 190,224,7, 282,313,10
9190 REM ---- default high scores: initials, score, site ----
9200 DATA "ARM", 6000, "TRANQUILITY", "ALD", 5000, "TRANQUILITY", "SHE", 4500, "FRA MAURO"
9210 DATA "SCO", 4000, "HADLEY RILLE", "MIT", 3500, "FRA MAURO", "IRW", 3000, "HADLEY RILLE"
9220 DATA "DUK", 2500, "TRANQUILITY", "ROO", 2000, "FRA MAURO", "WOR", 1500, "HADLEY RILLE"
9230 DATA "COL", 1000, "TRANQUILITY"
