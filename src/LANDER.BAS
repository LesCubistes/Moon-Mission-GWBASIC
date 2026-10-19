10 REM ==== MOON LANDING - choose a site, then land the lunar module ====
20 REM Keypad: 8/5 throttle up/down, 0 or SPACE engine off, 7 9 4 6 1 2 3 thrusters
30 COMMON SK%
40 DEFINT A-Z: KEY OFF: RANDOMIZE TIMER
50 REM -- every simple variable is created here, before any VARPTR/BLOAD --
60 X! = 0: Y! = 0: VX! = 0: VY! = 0: F! = 0: A! = 0: DT! = 0: T0! = 0: T1! = 0: ST! = 0
70 HT! = 0: PT! = 0: TT! = 0: GR! = 3: AM! = 7: DV! = .8: VYS! = 4: VXS! = 2
80 FM! = 800: BU! = 25: RF! = 4
90 XI = 0: YI = 0: OX = -1: OY = 0: FL = 0: OF = 0: PF = 0: OP = 0: TH = 0: K = 0: I = 0
100 LK = 0: B = 0: P = 0: NP = 0: LV = 1: S = 1: SC = 0: W = 0: AL = 0: LF = 0: RG = 0: MN = 0: Q = 0
105 CT = 0: D = 0: CX = 0: GC = 0: PX = 0: PY = 0: PO = 0: PZ = 0: R = 0: J = 0: Z = 0
107 FX = 0: FY = 0: FR = 0: GX = 0: GY = 0: DW = 0: ALM = 0: WD! = 0: T2! = 0: AT! = 0: RL! = 0
110 K$ = "": C$ = "": R$ = "": R2$ = "": M$ = ""
120 DIM H(639), SP(146), MK(146), BG(146), F1(146), F2(146), F3(146)
125 DIM Q1(146), Q2(146), Q3(146), Q4(146), Q6(146), Q7(146), Q9(146)
127 DIM B2(172), FB(450), C1(172), C2(172), C3(172), C4(172), C5(172), C6(172), C7(172)
128 DIM M1(172), M2(172), M3(172), M4(172), M5(172), M6(172), M7(172), EU(6), EV(6)
130 DIM LA(4), LB(4), LM(4), RX!(9), RY!(9), SN$(3), SD$(3), SA(3)
140 FOR I = 1 TO 9: READ RX!(I), RY!(I): NEXT I
150 FOR I = 1 TO 3: READ SN$(I), SD$(I), SA(I): NEXT I
155 FOR I = 1 TO 6: READ EU(I), EV(I): NEXT I
160 BLOAD "LMSHIP.SPR", VARPTR(SP(0))
170 BLOAD "LMMASK.SPR", VARPTR(MK(0))
180 BLOAD "FL1.SPR", VARPTR(F1(0)): BLOAD "FL2.SPR", VARPTR(F2(0)): BLOAD "FL3.SPR", VARPTR(F3(0))
182 BLOAD "RC1.SPR", VARPTR(Q1(0)): BLOAD "RC2.SPR", VARPTR(Q2(0)): BLOAD "RC3.SPR", VARPTR(Q3(0))
184 BLOAD "RC4.SPR", VARPTR(Q4(0)): BLOAD "RC6.SPR", VARPTR(Q6(0))
186 BLOAD "RC7.SPR", VARPTR(Q7(0)): BLOAD "RC9.SPR", VARPTR(Q9(0))
187 BLOAD "CP1.SPR", VARPTR(C1(0)): BLOAD "CP2.SPR", VARPTR(C2(0)): BLOAD "CP3.SPR", VARPTR(C3(0))
188 BLOAD "CP4.SPR", VARPTR(C4(0)): BLOAD "CP5.SPR", VARPTR(C5(0)): BLOAD "CP6.SPR", VARPTR(C6(0))
189 BLOAD "CP7.SPR", VARPTR(C7(0)): BLOAD "CM1.SPR", VARPTR(M1(0)): BLOAD "CM2.SPR", VARPTR(M2(0))
191 BLOAD "CM3.SPR", VARPTR(M3(0)): BLOAD "CM4.SPR", VARPTR(M4(0)): BLOAD "CM5.SPR", VARPTR(M5(0))
192 BLOAD "CM6.SPR", VARPTR(M6(0)): BLOAD "CM7.SPR", VARPTR(M7(0))
195 SCREEN 1, 0: COLOR 0, 1: PLAY "MB"
200 REM ==== landing site menu ====
210 OUT &H3D8, &H6: CLS
220 DEF SEG = &HB800: BLOAD "MOONBG.PIC", 0: DEF SEG
230 LINE (24, 40)-(295, 140), 0, BF: LINE (24, 40)-(295, 140), 1, B
240 OUT &H3D8, &HE: OUT &H3D9, 0
250 LOCATE 7, 11: PRINT "SELECT LANDING SITE";
260 FOR I = 1 TO 3
270 LOCATE 7 + 3 * I, 6: PRINT SN$(I);
280 LOCATE 8 + 3 * I, 6: IF SA(I) THEN PRINT SD$(I); ELSE PRINT "COMING SOON";
290 NEXT I
300 GOSUB 380
310 K$ = INKEY$: IF K$ = "" THEN 310
320 IF (K$ = CHR$(0) + "H" OR K$ = "8") AND S > 1 THEN S = S - 1: GOSUB 380
330 IF (K$ = CHR$(0) + "P" OR K$ = "2") AND S < 3 THEN S = S + 1: GOSUB 380
340 IF K$ = CHR$(27) THEN SK% = 1: CHAIN "MOON"
350 IF K$ <> CHR$(13) THEN 310
360 IF SA(S) = 0 THEN SOUND 200, 2: GOTO 310
370 LV = S: GOTO 1000
380 FOR I = 1 TO 3
390 LINE (36, 46 + 24 * I)-(283, 65 + 24 * I), -2 * (I = S), B
400 NEXT I: RETURN
1000 REM ==== load and start the level ====
1010 OUT &H3D8, &H6: CLS
1020 DEF SEG = &HB800: BLOAD "EASY.PIC", 0: DEF SEG
1030 BLOAD "EASY.MAP", VARPTR(H(0))
1040 RESTORE 9100: READ NP: FOR I = 1 TO NP: READ LA(I), LB(I), LM(I): NEXT I
1050 X! = 40: Y! = 24: VX! = 6: VY! = 1: F! = FM!: TH = 0: PF = 0: OX = -1: OF = -1: OP = -1
1060 OUT &H3D8, &HE: OUT &H3D9, 0
1070 LOCATE 1, 1: PRINT "FUEL";: LOCATE 1, 17: PRINT USING "SCORE ####"; SC;
1080 LOCATE 4, 13: PRINT SN$(LV);
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
2200 IF XI <> OX OR YI <> OY OR FL <> OF OR PF <> OP THEN GOSUB 5000
2210 IF T1! >= HT! THEN GOSUB 6000: HT! = T1! + .25
2220 IF TT! > 0 THEN IF T1! > TT! THEN LINE (96, 24)-(231, 31), 0, BF: TT! = 0
2230 GOTO 2010
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
4200 REM landed
4210 IF P THEN W = LM(P) ELSE W = 1
4220 B = W * (50 + INT(F! / 4)): SC = SC + B
4230 PLAY "T160O4L16CEG>C8"
4240 LINE (64, 60)-(255, 99), 0, BF: LINE (64, 60)-(255, 99), 1, B
4250 LOCATE 9, 11: PRINT "THE EAGLE HAS LANDED";
4260 LOCATE 10, 11: PRINT USING "PAD X#  BONUS #####"; W; B;
4270 LOCATE 12, 10: PRINT "ENTER=AGAIN  ESC=SITES";
4280 LOCATE 1, 17: PRINT USING "SCORE ####"; SC;
4290 GOTO 4500
4400 REM crashed: explain what happened
4410 LINE (64, 60)-(255, 99), 0, BF: LINE (64, 60)-(255, 99), 2, B
4420 LOCATE 9, 21 - LEN(R$) \ 2: PRINT R$;
4430 LOCATE 10, 21 - LEN(R2$) \ 2: PRINT R2$;
4440 LOCATE 12, 10: PRINT "ENTER=AGAIN  ESC=SITES";
4500 K$ = INKEY$: IF K$ = "" THEN 4500
4510 IF K$ = CHR$(27) THEN 200
4520 IF K$ = CHR$(13) THEN 1000
4530 GOTO 4500
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
9000 REM ---- thrusters: push x, push y for keys 1-9 (5 and 8 are throttle) ----
9010 DATA -.707,.707, 0,1, .707,.707, -1,0, 0,0, 1,0, -.707,-.707, 0,0, .707,-.707
9050 REM ---- landing sites ----
9060 DATA "TRANQUILITY BASE", "APOLLO 11 - EASY", 1
9070 DATA "FRA MAURO", "APOLLO 14 - MEDIUM", 0
9080 DATA "HADLEY RILLE", "APOLLO 15 - HARD", 0
9090 REM ---- debris directions for the explosion (x step, upward step) ----
9095 DATA -5,6, -3,8, -1,9, 2,9, 4,7, 5,5
9100 REM ---- Easy pads: left x, right x, multiplier ----
9110 DATA 3, 12,68,2, 140,184,3, 256,292,5
