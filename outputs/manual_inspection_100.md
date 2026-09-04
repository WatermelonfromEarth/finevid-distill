# FinQA ranking-data manual inspection (seed 42)

**Review status:** COMPLETE — 100/100 examples reviewed

This deterministic packet samples 100 train/development examples. The test split is excluded from qualitative inspection. Each case shows the question, every mapped positive, five negatives, and the untouched `qa.gold_inds` mapping.
## 001. [train] `ETR/2016/page_175.pdf-1`

**Question:** what are the implicit interest costs for the 2018 lease payments , in thousands?

**Mapped positives:**

- `table-row-2` (table[2]): 2018 | amount ( in thousands ): 17188
- `pre-text-14` (pre_text[14]): as of december 31 , 2016 , system energy , in connection with the grand gulf sale and leaseback transactions , had future minimum lease payments ( reflecting an implicit rate of 5.13% ( 5.13 % ) ) that are recorded as long-term debt , as follows : amount ( in thousands ) .

**Five negative candidates:**

- `pre-text-3` (pre_text[3]): in february 2017 the leases were terminated and the leased assets were conveyed to entergy louisiana .
- `table-row-5` (table[5]): 2021 | amount ( in thousands ): 17188
- `pre-text-13` (pre_text[13]): the amount was a net regulatory liability of $ 55.6 million and $ 55.6 million as of december 31 , 2016 and 2015 , respectively .
- `pre-text-11` (pre_text[11]): however , operating revenues include the recovery of the lease payments because the transactions are accounted for as a sale and leaseback for ratemaking purposes .
- `table-row-9` (table[9]): present value of net minimum lease payments | amount ( in thousands ): $ 34359

**Original gold annotations:**

```json
{
  "table_2": "the 2018 of amount ( in thousands ) is 17188 ;",
  "text_14": "as of december 31 , 2016 , system energy , in connection with the grand gulf sale and leaseback transactions , had future minimum lease payments ( reflecting an implicit rate of 5.13% ( 5.13 % ) ) that are recorded as long-term debt , as follows : amount ( in thousands ) ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 002. [train] `ETR/2016/page_424.pdf-2`

**Question:** what is the dollar amount in millions of letters of credit that can be issued under the august 2021 credit facility?

**Mapped positives:**

- `post-text-1` (post_text[1]): entergy texas has a credit facility in the amount of $ 150 million scheduled to expire in august 2021 .
- `post-text-2` (post_text[2]): the credit facility allows entergy texas to issue letters of credit against 50% ( 50 % ) of the borrowing capacity of the facility .

**Five negative candidates:**

- `pre-text-0` (pre_text[0]): entergy texas , inc .
- `pre-text-3` (pre_text[3]): also in addition to the contractual obligations , entergy texas has $ 15.6 million of unrecognized tax benefits and interest net of unused tax attributes and payments for which the timing of payments beyond 12 months cannot be reasonably estimated due to uncertainties in the timing of effective settlement of tax positions .
- `pre-text-11` (pre_text[11]): all debt and common and preferred stock issuances by entergy texas require prior regulatory approval .
- `pre-text-9` (pre_text[9]): sources of capital entergy texas 2019s sources to meet its capital requirements include : 2022 internally generated funds ; 2022 cash on hand ; 2022 debt or preferred stock issuances ; and 2022 bank financing under new or existing facilities .
- `pre-text-7` (pre_text[7]): management provides more information on long-term debt in note 5 to the financial statements .

**Original gold annotations:**

```json
{
  "text_16": "entergy texas has a credit facility in the amount of $ 150 million scheduled to expire in august 2021 .",
  "text_17": "the credit facility allows entergy texas to issue letters of credit against 50% ( 50 % ) of the borrowing capacity of the facility ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 003. [train] `GPN/2017/page_91.pdf-2`

**Question:** what was the percentage chaning in the total fair value of restricted stock and performance awards vested from 2016 to 2017?

**Mapped positives:**

- `post-text-0` (post_text[0]): the total fair value of restricted stock and performance awards vested was $ 33.7 million for the year ended december 31 , 2017 , $ 20.0 million for the 2016 fiscal transition period and $ 17.4 million and $ 15.0 million , respectively , for the years ended may 31 , 2016 and 2015 .

**Five negative candidates:**

- `table-row-8` (table[8]): forfeited | shares ( in thousands ): -70 ( 70 ) | weighted-averagegrant-datefair value: 34.69
- `table-row-1` (table[1]): unvested at may 31 2014 | shares ( in thousands ): 1754 | weighted-averagegrant-datefair value: $ 22.72
- `post-text-8` (post_text[8]): global payments inc .
- `table-row-4` (table[4]): forfeited | shares ( in thousands ): -212 ( 212 ) | weighted-averagegrant-datefair value: 27.03
- `pre-text-3` (pre_text[3]): after the three-year performance period , which concluded in october 2017 , one-third of the earned units converted to unrestricted common stock .

**Original gold annotations:**

```json
{
  "text_7": "the total fair value of restricted stock and performance awards vested was $ 33.7 million for the year ended december 31 , 2017 , $ 20.0 million for the 2016 fiscal transition period and $ 17.4 million and $ 15.0 million , respectively , for the years ended may 31 , 2016 and 2015 ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 004. [train] `CMCSA/2015/page_150.pdf-3`

**Question:** what was the average net income from 2013 to 2015

**Mapped positives:**

- `table-row-1` (table[1]): net income | 2015: $ 3624 | 2014: $ 3297 | 2013: $ 2122

**Five negative candidates:**

- `pre-text-0` (pre_text[0]): nbcuniversal media , llc consolidated statement of comprehensive income .
- `table-row-8` (table[8]): comprehensive income attributable to nbcuniversal | 2015: $ 3361 | 2014: $ 2972 | 2013: $ 2017
- `table-row-0` (table[0]): year ended december 31 ( in millions ) | 2015 | 2014 | 2013
- `table-row-5` (table[5]): comprehensive income | 2015: 3542 | 2014: 3154 | 2013: 2171
- `table-row-2` (table[2]): deferred gains ( losses ) on cash flow hedges net | 2015: -21 ( 21 ) | 2014: 25 | 2013: -5 ( 5 )

**Original gold annotations:**

```json
{
  "table_1": "year ended december 31 ( in millions ) the net income of 2015 is $ 3624 ; the net income of 2014 is $ 3297 ; the net income of 2013 is $ 2122 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 005. [train] `GS/2018/page_108.pdf-1`

**Question:** for asset category for positions accounted for at fair value , that are not included in var , in millions for 2018 and 2017 , what was the maximum equity value?

**Mapped positives:**

- `table-row-1` (table[1]): equity | as of december 2018: $ 1923 | as of december 2017: $ 2096

**Five negative candidates:**

- `post-text-2` (post_text[2]): 2030 debt positions include interests in funds that invest in corporate mezzanine and senior debt instruments , loans backed by commercial and residential real estate , corporate bank loans and other corporate debt , including acquired portfolios of distressed loans .
- `post-text-18` (post_text[18]): see note 6 to the consolidated financial statements for further information .
- `table-row-0` (table[0]): $ in millions | as of december 2018 | as of december 2017
- `post-text-22` (post_text[22]): 92 goldman sachs 2018 form 10-k .
- `post-text-5` (post_text[5]): 2030 these measures do not reflect the diversification effect across asset categories or across other market risk measures .

**Original gold annotations:**

```json
{
  "table_1": "$ in millions the equity of as of december 2018 is $ 1923 ; the equity of as of december 2017 is $ 2096 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 006. [train] `HUM/2013/page_52.pdf-2`

**Question:** what is the percentage of shares purchased in november concerning the whole 2013 year?

**Mapped positives:**

- `table-row-2` (table[2]): november 2013 | total number of shares purchased ( 1 ): 1191867 | average price paid per share: 98.18 | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ): 1191867 | dollar value of shares that may yet be purchased under the plans orprograms ( 1 ): 664123417
- `table-row-4` (table[4]): total | total number of shares purchased ( 1 ): 1994797 | average price paid per share: $ 100.56 | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ): 1994797 | dollar value of shares that may yet be purchased under the plans orprograms ( 1 ):

**Five negative candidates:**

- `post-text-1` (post_text[1]): under the current share repurchase authorization , shares may be purchased from time to time at prevailing prices in the open market , by block purchases , or in privately-negotiated transactions , subject to certain regulatory restrictions on volume , pricing , and timing .
- `post-text-2` (post_text[2]): as of february 1 , 2014 , the remaining authorized amount under the current authorization totaled approximately $ 580 million .
- `post-text-0` (post_text[0]): ( 1 ) as announced on may 1 , 2013 , in april 2013 , the board of directors replaced its previously approved share repurchase authorization of up to $ 1 billion with a current authorization for repurchases of up to $ 1 billion of our common shares exclusive of shares repurchased in connection with employee stock plans , expiring on june 30 , 2015 .
- `table-row-3` (table[3]): december 2013 | total number of shares purchased ( 1 ): 802930 | average price paid per share: 104.10 | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ): 802930 | dollar value of shares that may yet be purchased under the plans orprograms ( 1 ): 580555202
- `table-row-1` (table[1]): october 2013 | total number of shares purchased ( 1 ): 0 | average price paid per share: $ 0 | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ): 0 | dollar value of shares that may yet be purchased under the plans orprograms ( 1 ): $ 781118739

**Original gold annotations:**

```json
{
  "table_2": "period the november 2013 of total number of shares purchased ( 1 ) is 1191867 ; the november 2013 of average price paid per share is 98.18 ; the november 2013 of total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ) is 1191867 ; the november 2013 of dollar value of shares that may yet be purchased under the plans orprograms ( 1 ) is 664123417 ;",
  "table_4": "period the total of total number of shares purchased ( 1 ) is 1994797 ; the total of average price paid per share is $ 100.56 ; the total of total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ) is 1994797 ; the total of dollar value of shares that may yet be purchased under the plans orprograms ( 1 ) is ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 007. [train] `FITB/2008/page_69.pdf-4`

**Question:** what is the percentage change in capital expenditures from 2007 to 2008?

**Mapped positives:**

- `table-row-6` (table[6]): capital expenditures | 2008: 68 | 2007: 94

**Five negative candidates:**

- `pre-text-12` (pre_text[12]): the senior floating-rate bank notes due in 2013 are the obligations of a subsidiary bank .
- `pre-text-6` (pre_text[6]): subsidiary long-term borrowings the senior fixed-rate bank notes due from 2009 to 2019 are the obligations of a subsidiary bank .
- `post-text-1` (post_text[1]): since many of the commitments to extend credit may expire without being drawn upon , the total commitment amounts do not necessarily represent future cash flow requirements .
- `pre-text-27` (pre_text[27]): at december 31 , 2008 , fhlb advances have rates ranging from 0% ( 0 % ) to 8.34% ( 8.34 % ) , with interest payable monthly .
- `pre-text-22` (pre_text[22]): the obligations were issued to fnb statutory trusts i and ii , respectively .

**Original gold annotations:**

```json
{
  "table_6": "( $ in millions ) the capital expenditures of 2008 is 68 ; the capital expenditures of 2007 is 94 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 008. [train] `MAA/2017/page_89.pdf-1`

**Question:** considering the years 2015 and 2016 , what is the percentual increase observed in the total compensation expense under the stock plan?

**Mapped positives:**

- `pre-text-6` (pre_text[6]): total compensation expense under the stock plan was approximately $ 10.8 million , $ 12.2 million and $ 6.9 million for the years ended december 31 , 2017 , 2016 and 2015 , respectively .

**Five negative candidates:**

- `table-row-4` (table[4]): requisite service period | 2017: 3 years | 2016: 3 years | 2015: 3 years
- `pre-text-4` (pre_text[4]): effective january 1 , 2017 , the company adopted asu 2016-09 , improvements to employee share- based payment accounting , which allows employers to make a policy election to account for forfeitures as they occur .
- `pre-text-9` (pre_text[9]): this cost is expected to be recognized over the remaining weighted average period of 1.2 years .
- `table-row-3` (table[3]): volatility | 2017: 20.43% ( 20.43 % ) - 21.85% ( 21.85 % ) | 2016: 18.41% ( 18.41 % ) - 19.45% ( 19.45 % ) | 2015: 15.41% ( 15.41 % ) - 16.04% ( 16.04 % )
- `pre-text-11` (pre_text[11]): information concerning grants under the stock plan is listed below .

**Original gold annotations:**

```json
{
  "text_6": "total compensation expense under the stock plan was approximately $ 10.8 million , $ 12.2 million and $ 6.9 million for the years ended december 31 , 2017 , 2016 and 2015 , respectively ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 009. [train] `UNP/2012/page_47.pdf-3`

**Question:** what is the estimated growth rate in net periodic pension cost from 2012 to 2013?

**Mapped positives:**

- `table-row-1` (table[1]): net periodic pension cost | est.2013: $ 111 | 2012: $ 89 | 2011: $ 78 | 2010: $ 51

**Five negative candidates:**

- `post-text-1` (post_text[1]): the increase is driven mainly by a decrease in the discount rate to 3.78% ( 3.78 % ) , our net periodic opeb expense is expected to increase to approximately $ 15 million in 2013 from $ 13 million in 2012 .
- `post-text-8` (post_text[8]): forward-looking statements and information reflect the good faith consideration by management of currently available information , and may be based on underlying assumptions believed to be reasonable under the circumstances .
- `post-text-15` (post_text[15]): if we do update one or more forward-looking .
- `post-text-9` (post_text[9]): however , such information and assumptions ( and , therefore , such forward-looking statements and information ) are or may be subject to variables or unknown or unforeseeable events or circumstances over which management has little or no influence or control .
- `post-text-0` (post_text[0]): our net periodic pension cost is expected to increase to approximately $ 111 million in 2013 from $ 89 million in 2012 .

**Original gold annotations:**

```json
{
  "table_1": "millions the net periodic pension cost of est.2013 is $ 111 ; the net periodic pension cost of 2012 is $ 89 ; the net periodic pension cost of 2011 is $ 78 ; the net periodic pension cost of 2010 is $ 51 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 010. [train] `PNC/2014/page_156.pdf-1`

**Question:** what were total specific reserves in the alll in billions at december 31 , 2014 and december 31 , 2013 for the total tdr portfolio?

**Mapped positives:**

- `pre-text-6` (pre_text[6]): the level of any subsequent defaults will likely be affected by future economic conditions .
- `pre-text-8` (pre_text[8]): we held specific reserves in the alll of $ .4 billion and $ .5 billion at december 31 , 2014 and december 31 , 2013 , respectively , for the total tdr portfolio .

**Five negative candidates:**

- `table-row-7` (table[7]): total tdrs | december 312014: $ 2583 | december 312013: $ 2739
- `table-row-6` (table[6]): credit card | december 312014: 130 | december 312013: 166
- `pre-text-0` (pre_text[0]): troubled debt restructurings ( tdrs ) a tdr is a loan whose terms have been restructured in a manner that grants a concession to a borrower experiencing financial difficulty .
- `post-text-12` (post_text[12]): for example , if there is principal forgiveness in conjunction with lower interest rate and postponement of amortization , the type of concession will be reported as principal forgiveness .
- `table-row-4` (table[4]): nonperforming | december 312014: $ 1370 | december 312013: $ 1511

**Original gold annotations:**

```json
{
  "text_6": "the level of any subsequent defaults will likely be affected by future economic conditions .",
  "text_8": "we held specific reserves in the alll of $ .4 billion and $ .5 billion at december 31 , 2014 and december 31 , 2013 , respectively , for the total tdr portfolio ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 011. [train] `MRO/2004/page_57.pdf-1`

**Question:** by how much did the effective tax rate decrease from 2002 to 2004?

**Mapped positives:**

- `table-row-5` (table[5]): effective tax rate | 2004: 36.6% ( 36.6 % ) | 2003: 36.6% ( 36.6 % ) | 2002: 42.1% ( 42.1 % )

**Five negative candidates:**

- `pre-text-23` (pre_text[23]): the higher rate in 2002 was due to the united kingdom enactment of a supplementary 10 percent tax on profits from the north sea oil and gas production , retroactively effective to april 17 , 2002 .
- `post-text-1` (post_text[1]): increased the effective tax rate 7.0 percent in .
- `pre-text-4` (pre_text[4]): the increases are primarily in the rm&t segment and result from higher acquisition costs for crude oil , refined products , refinery charge and blend feedstocks and increased manufacturing expenses .
- `pre-text-21` (pre_text[21]): provision for income taxes increased by $ 143 million in 2004 from 2003 and by $ 215 million in 2003 from 2002 , primarily due to $ 388 million and $ 720 million increases in income before income taxes .
- `pre-text-20` (pre_text[20]): minority interest in loss of equatorial guinea lng holdings limited , which represents gepetrol 2019s 25 percent ownership interest , was $ 7 million in 2004 , primarily resulting from gepetrol 2019s share of start-up costs associated with the lng project in equatorial guinea .

**Original gold annotations:**

```json
{
  "table_5": "the effective tax rate of 2004 is 36.6% ( 36.6 % ) ; the effective tax rate of 2003 is 36.6% ( 36.6 % ) ; the effective tax rate of 2002 is 42.1% ( 42.1 % ) ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 012. [train] `EMN/2007/page_111.pdf-1`

**Question:** what was the ratio of the investment prior to sale to the pre-tax gain on the sale

**Mapped positives:**

- `pre-text-26` (pre_text[26]): the book value of the investment prior to sale was $ 246 million , and the company recorded a pre-tax gain on the sale of $ 171 million .

**Five negative candidates:**

- `pre-text-15` (pre_text[15]): at december 31 , 2007 , the company 2019s investment in tx energy was approximately $ 26 million .
- `pre-text-19` (pre_text[19]): the company intends to take a 25 percent or greater equity position in the project , provide operations , maintenance , and other site management services , and purchase methanol under a long-term contract .
- `pre-text-14` (pre_text[14]): this joint venture in the development stage is accounted for under the equity method , and is included in other noncurrent assets .
- `pre-text-12` (pre_text[12]): shaw group and goldman , sachs & co. , to jointly develop the industrial gasification facility in beaumont , texas through tx energy , llc ( "tx energy" ) .
- `pre-text-9` (pre_text[9]): in october 2007 , the company entered into an agreement with green rock energy , l.l.c .

**Original gold annotations:**

```json
{
  "text_26": "the book value of the investment prior to sale was $ 246 million , and the company recorded a pre-tax gain on the sale of $ 171 million ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 013. [train] `EW/2016/page_72.pdf-1`

**Question:** what percentage of the settlement was due to past damages?

**Mapped positives:**

- `table-row-3` (table[3]): total | $ 754.3: $ 1070.0

**Five negative candidates:**

- `post-text-0` (post_text[0]): .
- `pre-text-7` (pre_text[7]): the company is assessing all of the potential impacts of the revenue recognition guidance and has not yet selected an adoption method .
- `pre-text-3` (pre_text[3]): the core principle of the guidance is that an entity should recognize revenue to depict the transfer of promised goods or services to customers in an amount that reflects the consideration to which the entity expects to be entitled in exchange for those goods or services .
- `pre-text-11` (pre_text[11]): 3 .
- `table-row-2` (table[2]): covenant not to sue | $ 754.3: 77.7

**Original gold annotations:**

```json
{
  "table_3": "past damages the total of $ 754.3 is $ 1070.0 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 014. [train] `AAPL/2007/page_70.pdf-3`

**Question:** what was the percentage change in the allowance for doubtful accounts from 2006 to 2007?

**Mapped positives:**

- `table-row-4` (table[4]): ending allowance balance | september 29 2007: $ 47 | september 30 2006: $ 52 | september 24 2005: $ 46

**Five negative candidates:**

- `post-text-5` (post_text[5]): foreign currency forward and option contracts are used to offset the foreign exchange risk on certain existing assets and liabilities and to hedge the foreign exchange risk on expected future cash flows on certain forecasted revenue and cost of sales .
- `table-row-2` (table[2]): charged to costs and expenses | september 29 2007: 12 | september 30 2006: 17 | september 24 2005: 8
- `pre-text-0` (pre_text[0]): notes to consolidated financial statements ( continued ) note 2 2014financial instruments ( continued ) covered by collateral , third-party flooring arrangements , or credit insurance are outstanding with the company 2019s distribution and retail channel partners .
- `post-text-7` (post_text[7]): the company records all derivatives on the balance sheet at fair value. .
- `pre-text-1` (pre_text[1]): one customer accounted for approximately 11% ( 11 % ) of trade receivables as of september 29 , 2007 , while no customers accounted for more than 10% ( 10 % ) of trade receivables as of september 30 , 2006 .

**Original gold annotations:**

```json
{
  "table_4": "the ending allowance balance of september 29 2007 is $ 47 ; the ending allowance balance of september 30 2006 is $ 52 ; the ending allowance balance of september 24 2005 is $ 46 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 015. [train] `C/2009/page_38.pdf-3`

**Question:** what was the net change in the private equity and equity investments from 2008 to 2009 in millions

**Mapped positives:**

- `table-row-1` (table[1]): private equity and equity investments | pretax revenue 2009: $ 201 | pretax revenue 2008: $ -377 ( 377 )

**Five negative candidates:**

- `pre-text-6` (pre_text[6]): excluding the 2008 repositioning and restructuring charges and the 2009 litigation reserve release , operating expenses declined 11% ( 11 % ) or $ 1.6 billion , mainly as a result of headcount reductions and benefits from expense management .
- `post-text-7` (post_text[7]): 2010 outlook the 2010 outlook for s&b will depend on the level of client activity and on macroeconomic conditions , market valuations and volatility , interest rates and other market factors .
- `pre-text-2` (pre_text[2]): the growth in revenue in the early part of the year was mainly due to a $ 7.1 billion increase in fixed income markets , reflecting strong trading opportunities across all asset classes in the first half of 2009 , and a $ 1.5 billion increase in investment banking revenue primarily from increases in debt and equity underwriting activities reflecting higher transaction volumes from depressed 2008 levels .
- `table-row-4` (table[4]): cva on citi debt liabilities under fair value option | pretax revenue 2009: -3974 ( 3974 ) | pretax revenue 2008: 4325
- `pre-text-14` (pre_text[14]): excluding the 2008 and 2007 repositioning and restructuring charges and the 2007 litigation reserve reversal , operating expenses decreased by 7% ( 7 % ) or $ 1.1 billion driven by headcount reduction and lower performance-based incentives .

**Original gold annotations:**

```json
{
  "table_1": "in millions of dollars the private equity and equity investments of pretax revenue 2009 is $ 201 ; the private equity and equity investments of pretax revenue 2008 is $ -377 ( 377 ) ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 016. [train] `STT/2008/page_116.pdf-2`

**Question:** what is the percentage change in conduit assets in unites states from 2007 to 2008?

**Mapped positives:**

- `table-row-1` (table[1]): united states | 2008 amount: $ 11.09 | 2008 percent of total conduit assets: 46% ( 46 % ) | 2008 amount: $ 12.14 | percent of total conduit assets: 42% ( 42 % )

**Five negative candidates:**

- `post-text-16` (post_text[16]): conduit-issued commercial paper had been sold to the cpff .
- `post-text-17` (post_text[17]): the cpff is scheduled to expire on october 31 , 2009 .
- `post-text-12` (post_text[12]): the conduits generally sell commercial paper to independent third-party investors .
- `post-text-20` (post_text[20]): aggregate first-loss notes outstanding at december 31 , 2008 for the four conduits totaled $ 67 million , compared to $ 32 million at december 31 , 2007 .
- `post-text-15` (post_text[15]): in addition , approximately $ 5.70 billion of u.s .

**Original gold annotations:**

```json
{
  "table_1": "( dollars in billions ) the united states of 2008 amount is $ 11.09 ; the united states of 2008 percent of total conduit assets is 46% ( 46 % ) ; the united states of 2008 amount is $ 12.14 ; the united states of percent of total conduit assets is 42% ( 42 % ) ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 017. [train] `C/2015/page_314.pdf-2`

**Question:** what was the difference in percentage cumulative total return of citi common stock compared to the s&p financials for the five years ended 31-dec-2015?

**Mapped positives:**

- `table-row-1` (table[1]): 31-dec-2010 | citi: 100.00 | s&p 500: 100.00 | s&p financials: 100.00
- `table-row-6` (table[6]): 31-dec-2015 | citi: 110.14 | s&p 500: 180.75 | s&p financials: 164.39

**Five negative candidates:**

- `table-row-4` (table[4]): 31-dec-2013 | citi: 110.49 | s&p 500: 156.82 | s&p financials: 144.90
- `table-row-3` (table[3]): 31-dec-2012 | citi: 83.81 | s&p 500: 118.45 | s&p financials: 106.84
- `table-row-2` (table[2]): 30-dec-2011 | citi: 55.67 | s&p 500: 102.11 | s&p financials: 82.94
- `post-text-0` (post_text[0]): .
- `pre-text-1` (pre_text[1]): the graph and table assume that $ 100 was invested on december 31 , 2010 in citi 2019s common stock , the s&p 500 index and the s&p financial index , and that all dividends were reinvested .

**Original gold annotations:**

```json
{
  "table_1": "date the 31-dec-2010 of citi is 100.00 ; the 31-dec-2010 of s&p 500 is 100.00 ; the 31-dec-2010 of s&p financials is 100.00 ;",
  "table_6": "date the 31-dec-2015 of citi is 110.14 ; the 31-dec-2015 of s&p 500 is 180.75 ; the 31-dec-2015 of s&p financials is 164.39 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 018. [train] `MSI/2006/page_39.pdf-1`

**Question:** in 2006 what was the percent of the total number of shares purchased as part of publicly announced plans or programs on or after 11/26/2006

**Mapped positives:**

- `table-row-3` (table[3]): 11/26/06 to 12/31/06 | ( a ) total number of shares purchased ( 1 ) ( 4 ): 16430030 | ( b ) average price paid per share ( 1 ) ( 2 ): $ 21.29 | ( c ) total number of shares purchased as part of publicly announced plans or programs ( 3 ) ( 4 ): 16425602 | ( d ) maximum number ( or approximate dollar value ) of shares that may yet be purchased under the plans or programs ( 5 ): $ 3800689819
- `table-row-4` (table[4]): total | ( a ) total number of shares purchased ( 1 ) ( 4 ): 32048472 | ( b ) average price paid per share ( 1 ) ( 2 ): $ 21.83 | ( c ) total number of shares purchased as part of publicly announced plans or programs ( 3 ) ( 4 ): 32038760 | ( d ) maximum number ( or approximate dollar value ) of shares that may yet be purchased under the plans or programs ( 5 ):

**Five negative candidates:**

- `pre-text-2` (pre_text[2]): the remainder of the response to this item incorporates by reference note 16 , ""quarterly and other financial data ( unaudited ) '' of the notes to consolidated financial statements appearing under ""item 8 : financial statements and supplementary data'' .
- `post-text-1` (post_text[1]): ( 2 ) average price paid per share of stock repurchased under the 2006 stock repurchase program is execution price , excluding commissions paid to brokers .
- `post-text-5` (post_text[5]): under the asb the company immediately paid $ 1.2 billion and received an initial 37.9 million shares in july followed by an additional 11.3 million shares in august .
- `table-row-1` (table[1]): 10/1/06 to 10/28/06 | ( a ) total number of shares purchased ( 1 ) ( 4 ): 5284 | ( b ) average price paid per share ( 1 ) ( 2 ): $ 25.82 | ( c ) total number of shares purchased as part of publicly announced plans or programs ( 3 ) ( 4 ): 0 | ( d ) maximum number ( or approximate dollar value ) of shares that may yet be purchased under the plans or programs ( 5 ): $ 4500000000
- `table-row-0` (table[0]): period | ( a ) total number of shares purchased ( 1 ) ( 4 ) | ( b ) average price paid per share ( 1 ) ( 2 ) | ( c ) total number of shares purchased as part of publicly announced plans or programs ( 3 ) ( 4 ) | ( d ) maximum number ( or approximate dollar value ) of shares that may yet be purchased under the plans or programs ( 5 )

**Original gold annotations:**

```json
{
  "table_3": "period the 11/26/06 to 12/31/06 of ( a ) total number of shares purchased ( 1 ) ( 4 ) is 16430030 ; the 11/26/06 to 12/31/06 of ( b ) average price paid per share ( 1 ) ( 2 ) is $ 21.29 ; the 11/26/06 to 12/31/06 of ( c ) total number of shares purchased as part of publicly announced plans or programs ( 3 ) ( 4 ) is 16425602 ; the 11/26/06 to 12/31/06 of ( d ) maximum number ( or approximate dollar value ) of shares that may yet be purchased under the plans or programs ( 5 ) is $ 3800689819 ;",
  "table_4": "period the total of ( a ) total number of shares purchased ( 1 ) ( 4 ) is 32048472 ; the total of ( b ) average price paid per share ( 1 ) ( 2 ) is $ 21.83 ; the total of ( c ) total number of shares purchased as part of publicly announced plans or programs ( 3 ) ( 4 ) is 32038760 ; the total of ( d ) maximum number ( or approximate dollar value ) of shares that may yet be purchased under the plans or programs ( 5 ) is ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 019. [train] `HIG/2008/page_113.pdf-2`

**Question:** what is the net income reported in 2007 , ( in millions ) ?

**Mapped positives:**

- `table-row-1` (table[1]): basic earnings ( losses ) per share | 2008: $ -8.99 ( 8.99 ) | 2007: $ 9.32 | 2006: $ 8.89
- `table-row-4` (table[4]): weighted average common shares outstanding and dilutive potential common shares ( diluted ) | 2008: 306.7 | 2007: 319.1 | 2006: 315.9
- `pre-text-12` (pre_text[12]): actual results are likely to differ , and in the past have differed , materially from those forecast by the company , depending on the outcome of various factors , including , but not limited to , those set forth in each 201coutlook 201d section and in item 1a , risk factors .
- `table-row-3` (table[3]): weighted average common shares outstanding ( basic ) | 2008: 306.7 | 2007: 316.3 | 2006: 308.8

**Five negative candidates:**

- `pre-text-5` (pre_text[5]): these amounts included benefits related to true- ups of prior years 2019 tax returns of $ 4 , $ 0 and $ 7 in 2008 , 2007 and 2006 respectively .
- `pre-text-15` (pre_text[15]): see risk factors in item 1a .
- `pre-text-0` (pre_text[0]): table of contents the company receives a foreign tax credit ( 201cftc 201d ) against its u.s .
- `table-row-2` (table[2]): diluted earnings ( losses ) per share | 2008: $ -8.99 ( 8.99 ) | 2007: $ 9.24 | 2006: $ 8.69
- `pre-text-24` (pre_text[24]): significant declines in equity markets and increased equity market volatility are also likely to continue to impact the cost and effectiveness of our gmwb hedging program .

**Original gold annotations:**

```json
{
  "table_1": "the basic earnings ( losses ) per share of 2008 is $ -8.99 ( 8.99 ) ; the basic earnings ( losses ) per share of 2007 is $ 9.32 ; the basic earnings ( losses ) per share of 2006 is $ 8.89 ;",
  "table_4": "the weighted average common shares outstanding and dilutive potential common shares ( diluted ) of 2008 is 306.7 ; the weighted average common shares outstanding and dilutive potential common shares ( diluted ) of 2007 is 319.1 ; the weighted average common shares outstanding and dilutive potential common shares ( diluted ) of 2006 is 315.9 ;",
  "text_12": "actual results are likely to differ , and in the past have differed , materially from those forecast by the company , depending on the outcome of various factors , including , but not limited to , those set forth in each 201coutlook 201d section and in item 1a , risk factors .",
  "table_3": "the weighted average common shares outstanding ( basic ) of 2008 is 306.7 ; the weighted average common shares outstanding ( basic ) of 2007 is 316.3 ; the weighted average common shares outstanding ( basic ) of 2006 is 308.8 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 020. [train] `RL/2014/page_13.pdf-2`

**Question:** what percentage of factory stores as of march 29 , 2014 are in asia?

**Mapped positives:**

- `table-row-3` (table[3]): asia ( a ) | factory stores: 35
- `table-row-4` (table[4]): total | factory stores: 235

**Five negative candidates:**

- `post-text-14` (post_text[14]): e-commerce websites in addition to our stores , our retail segment sells products online through our e-commerce channel , which includes : 2022 our north american e-commerce sites located at www.ralphlauren.com and www.clubmonaco.com , as well as our club monaco site in canada located at www.clubmonaco.ca ; 2022 our ralph lauren e-commerce sites in europe , including www.ralphlauren.co.uk ( servicing the united kingdom ) , www.ralphlauren.fr ( servicing belgium , france , italy , luxembourg , the netherlands , portugal , and spain ) , and www.ralphlauren.de ( servicing germany and austria ) ; and 2022 our ralph lauren e-commerce sites in asia , including www.ralphlauren.co.jp servicing japan and www.ralphlauren.co.kr servicing south korea .
- `post-text-5` (post_text[5]): our factory stores in asia offer selections of our menswear , womenswear , childrenswear , accessories , and fragrances .
- `post-text-16` (post_text[16]): while investing in e-commerce operations remains a primary focus , it is an extension of our investment in the integrated omni-channel strategy used to operate our overall retail business , in which our e-commerce operations are interdependent with our physical stores .
- `post-text-3` (post_text[3]): our factory stores in europe offer selections of our menswear , womenswear , childrenswear , accessories , home furnishings , and fragrances .
- `post-text-17` (post_text[17]): our club monaco e-commerce sites in the u.s .

**Original gold annotations:**

```json
{
  "table_3": "location the asia ( a ) of factory stores is 35 ;",
  "table_4": "location the total of factory stores is 235 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 021. [train] `AOS/2016/page_19.pdf-2`

**Question:** what was the difference in total return for the five year period ended 12/31/16 between a . o . smith corporation and the russell 1000 index?

**Mapped positives:**

- `table-row-1` (table[1]): a . o . smith corporation | baseperiod 12/31/11: 100.0 | baseperiod 12/31/12: 159.5 | baseperiod 12/31/13: 275.8 | baseperiod 12/31/14: 292.0 | baseperiod 12/31/15: 401.0 | 12/31/16: 501.4
- `table-row-3` (table[3]): russell 1000 index | baseperiod 12/31/11: 100.0 | baseperiod 12/31/12: 116.4 | baseperiod 12/31/13: 155.0 | baseperiod 12/31/14: 175.4 | baseperiod 12/31/15: 177.0 | 12/31/16: 198.4

**Five negative candidates:**

- `pre-text-0` (pre_text[0]): the graph below shows a five-year comparison of the cumulative shareholder return on our common stock with the cumulative total return of the standard & poor 2019s ( s&p ) mid cap 400 index and the russell 1000 index , both of which are published indices .
- `table-row-2` (table[2]): s&p mid cap 400 index | baseperiod 12/31/11: 100.0 | baseperiod 12/31/12: 117.9 | baseperiod 12/31/13: 157.4 | baseperiod 12/31/14: 172.8 | baseperiod 12/31/15: 169.0 | 12/31/16: 204.1
- `pre-text-1` (pre_text[1]): comparison of five-year cumulative total return from december 31 , 2011 to december 31 , 2016 assumes $ 100 invested with reinvestment of dividends period indexed returns .
- `post-text-0` (post_text[0]): 2011 2012 2013 2014 2015 2016 smith ( a o ) corp s&p midcap 400 index russell 1000 index .
- `table-row-0` (table[0]): company/index | baseperiod 12/31/11 | baseperiod 12/31/12 | baseperiod 12/31/13 | baseperiod 12/31/14 | baseperiod 12/31/15 | 12/31/16

**Original gold annotations:**

```json
{
  "table_1": "company/index the a . o . smith corporation of baseperiod 12/31/11 is 100.0 ; the a . o . smith corporation of baseperiod 12/31/12 is 159.5 ; the a . o . smith corporation of baseperiod 12/31/13 is 275.8 ; the a . o . smith corporation of baseperiod 12/31/14 is 292.0 ; the a . o . smith corporation of baseperiod 12/31/15 is 401.0 ; the a . o . smith corporation of 12/31/16 is 501.4 ;",
  "table_3": "company/index the russell 1000 index of baseperiod 12/31/11 is 100.0 ; the russell 1000 index of baseperiod 12/31/12 is 116.4 ; the russell 1000 index of baseperiod 12/31/13 is 155.0 ; the russell 1000 index of baseperiod 12/31/14 is 175.4 ; the russell 1000 index of baseperiod 12/31/15 is 177.0 ; the russell 1000 index of 12/31/16 is 198.4 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 022. [train] `IP/2013/page_62.pdf-2`

**Question:** in 2012 what percentage of printing papers sales where attributable to north american printing papers net sales?

**Mapped positives:**

- `table-row-1` (table[1]): sales | 2013: $ 6205 | 2012: $ 6230 | 2011: $ 6215
- `post-text-0` (post_text[0]): north american printing papers net sales were $ 2.6 billion in 2013 , $ 2.7 billion in 2012 and $ 2.8 billion in 2011. .

**Five negative candidates:**

- `pre-text-9` (pre_text[9]): brazilian industrial packaging includes the results of orsa international paper embalagens s.a. , a corrugated packaging producer in which international paper acquired a 75% ( 75 % ) share in january 2013 .
- `pre-text-34` (pre_text[34]): printing papers .
- `pre-text-2` (pre_text[2]): in europe , sales volumes decreased slightly due to continuing weak demand for packaging in the industrial markets , and lower demand for packaging in the agricultural markets resulting from poor weather conditions .
- `pre-text-23` (pre_text[23]): principal cost drivers include manufacturing efficiency , raw material and energy costs and freight costs .
- `table-row-0` (table[0]): in millions | 2013 | 2012 | 2011

**Original gold annotations:**

```json
{
  "table_1": "in millions the sales of 2013 is $ 6205 ; the sales of 2012 is $ 6230 ; the sales of 2011 is $ 6215 ;",
  "text_35": "north american printing papers net sales were $ 2.6 billion in 2013 , $ 2.7 billion in 2012 and $ 2.8 billion in 2011. ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 023. [train] `VRTX/2006/page_112.pdf-1`

**Question:** what was the average price per share , in dollars , of the stock the company sold in august 2006?

**Mapped positives:**

- `pre-text-3` (pre_text[3]): when the altus securities trading restrictions expired , the company sold the 817749 shares of altus common stock for approximately $ 11.7 million , resulting in a realized gain of approximately $ 7.7 million in august 2006 .

**Five negative candidates:**

- `pre-text-7` (pre_text[7]): in the fourth quarter of 2006 the company sold the altus warrants for approximately $ 18.3 million , resulting in a realized loss of $ 0.7 million .
- `table-row-5` (table[5]): total | 2006: $ 91359 | 2005: $ 42061
- `pre-text-15` (pre_text[15]): the term of the kendall square lease began january 1 , 2003 and lease payments commenced in may 2003 .
- `pre-text-12` (pre_text[12]): accrued expenses and other current liabilities accrued expenses and other current liabilities consist of the following at december 31 ( in thousands ) : k .
- `pre-text-10` (pre_text[10]): the company 2019s cost basis carrying value in its outstanding equity and warrants of altus was $ 18.9 million at december 31 , 2005 .

**Original gold annotations:**

```json
{
  "text_3": "when the altus securities trading restrictions expired , the company sold the 817749 shares of altus common stock for approximately $ 11.7 million , resulting in a realized gain of approximately $ 7.7 million in august 2006 ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 024. [train] `MRO/2012/page_39.pdf-3`

**Question:** by what percentage did the average price of wti crude oil increase from 2010 to 2012?

**Mapped positives:**

- `table-row-1` (table[1]): wti crude oil ( dollars per bbl ) | 2012: $ 94.15 | 2011: $ 95.11 | 2010: $ 79.61

**Five negative candidates:**

- `pre-text-14` (pre_text[14]): spin-off downstream business on june 30 , 2011 , the spin-off of marathon 2019s downstream business was completed , creating two independent energy companies : marathon oil and mpc .
- `pre-text-2` (pre_text[2]): our operations are organized into three reportable segments : 2022 e&p which explores for , produces and markets liquid hydrocarbons and natural gas on a worldwide basis .
- `pre-text-20` (pre_text[20]): the following table lists benchmark crude oil and natural gas price annual averages for the past three years. .
- `post-text-4` (post_text[4]): liquid hydrocarbon realizations to differ from the wti benchmark .
- `pre-text-17` (pre_text[17]): activities related to the downstream business have been treated as discontinued operations in 2011 and 2010 ( see item 8 .

**Original gold annotations:**

```json
{
  "table_1": "benchmark the wti crude oil ( dollars per bbl ) of 2012 is $ 94.15 ; the wti crude oil ( dollars per bbl ) of 2011 is $ 95.11 ; the wti crude oil ( dollars per bbl ) of 2010 is $ 79.61 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 025. [train] `MAS/2017/page_37.pdf-3`

**Question:** what was the percent of the increase in the operating profit as reported from 2016 to 2017

**Mapped positives:**

- `table-row-1` (table[1]): operating profit as reported | 2017: $ 1169 | 2016: $ 1053 | 2015: $ 914

**Five negative candidates:**

- `table-row-5` (table[5]): operating profit margins as reported | 2017: 15.3% ( 15.3 % ) | 2016: 14.3% ( 14.3 % ) | 2015: 12.8% ( 12.8 % )
- `pre-text-5` (pre_text[5]): net sales for 2015 were also positively affected by net selling price increases of plumbing products , cabinets and windows , as well as sales mix of north american cabinets and windows .
- `table-row-3` (table[3]): gain from sale of property and equipment | 2017: 2014 | 2016: 2014 | 2015: -5 ( 5 )
- `table-row-6` (table[6]): operating profit margins as adjusted | 2017: 15.3% ( 15.3 % ) | 2016: 14.6% ( 14.6 % ) | 2015: 13.0% ( 13.0 % )
- `pre-text-13` (pre_text[13]): the following table reconciles reported operating profit to operating profit , as adjusted to exclude certain items , dollars in millions: .

**Original gold annotations:**

```json
{
  "table_1": "the operating profit as reported of 2017 is $ 1169 ; the operating profit as reported of 2016 is $ 1053 ; the operating profit as reported of 2015 is $ 914 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 026. [train] `AMT/2008/page_105.pdf-4`

**Question:** for ati what was the percent of the increase in the shares bought by employees from 2007 to 2008

**Mapped positives:**

- `pre-text-1` (pre_text[1]): during the 2008 , 2007 and 2006 offering periods employees purchased 55764 , 48886 and 53210 shares , respectively , at weighted average prices per share of $ 30.08 , $ 33.93 and $ 24.98 , respectively .

**Five negative candidates:**

- `post-text-2` (post_text[2]): these warrants became exercisable on january 29 , 2006 at an exercise price of $ 0.01 per share .
- `post-text-13` (post_text[13]): these warrants will expire on february 10 , 2010 .
- `pre-text-0` (pre_text[0]): american tower corporation and subsidiaries notes to consolidated financial statements 2014 ( continued ) from december 1 through may 31 of each year .
- `pre-text-3` (pre_text[3]): the weighted average fair value for the espp shares purchased during 2008 , 2007 and 2006 were $ 7.89 , $ 9.09 and $ 6.79 , respectively .
- `table-row-2` (table[2]): weighted average risk-free interest rate | 2008: 2.58% ( 2.58 % ) | 2007: 5.02% ( 5.02 % ) | 2006: 5.08% ( 5.08 % )

**Original gold annotations:**

```json
{
  "text_1": "during the 2008 , 2007 and 2006 offering periods employees purchased 55764 , 48886 and 53210 shares , respectively , at weighted average prices per share of $ 30.08 , $ 33.93 and $ 24.98 , respectively ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 027. [train] `UNP/2006/page_33.pdf-2`

**Question:** what was the net change in other income from 2004 to 2005 in millions?

**Mapped positives:**

- `table-row-1` (table[1]): other income | 2006: $ 118 | 2005: $ 145 | 2004: $ 88 | % (  % ) change 2006 v 2005: ( 19 ) % (  % ) | % (  % ) change 2005 v 2004: 65% ( 65 % )

**Five negative candidates:**

- `post-text-7` (post_text[7]): income taxes were greater in 2005 than 2004 due to higher pre-tax income partially offset by a previously reported reduction in income tax expense .
- `post-text-4` (post_text[4]): income taxes 2013 income tax expense was $ 509 million higher in 2006 than 2005 .
- `post-text-8` (post_text[8]): in our quarterly report on form 10-q for the quarter ended june 30 , 2005 , we reported that the corporation analyzed the impact that final settlements of pre-1995 tax years had on previously recorded estimates of deferred tax assets and liabilities .
- `table-row-0` (table[0]): millions of dollars | 2006 | 2005 | 2004 | % (  % ) change 2006 v 2005 | % (  % ) change 2005 v 2004
- `post-text-1` (post_text[1]): in 2005 , other income increased largely as a result of higher gains from real estate sales partially offset by higher expenses due to rising interest rates associated with our sale of receivables program .

**Original gold annotations:**

```json
{
  "table_1": "millions of dollars the other income of 2006 is $ 118 ; the other income of 2005 is $ 145 ; the other income of 2004 is $ 88 ; the other income of % ( % ) change 2006 v 2005 is ( 19 ) % ( % ) ; the other income of % ( % ) change 2005 v 2004 is 65% ( 65 % ) ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 028. [train] `AAPL/2015/page_68.pdf-2`

**Question:** what percentage of future minimum lease payments under noncancelable operating leases are due in 2018?

**Mapped positives:**

- `table-row-2` (table[2]): 2018 | $ 772: 744
- `table-row-6` (table[6]): total | $ 772: $ 6271

**Five negative candidates:**

- `post-text-0` (post_text[0]): other commitments the company utilizes several outsourcing partners to manufacture sub-assemblies for the company 2019s products and to perform final assembly and testing of finished products .
- `post-text-7` (post_text[7]): | 2015 form 10-k | 65 .
- `table-row-5` (table[5]): thereafter | $ 772: 2592
- `pre-text-7` (pre_text[7]): substantially all of the company 2019s hardware products are manufactured by outsourcing partners that are located primarily in asia .
- `post-text-4` (post_text[4]): where appropriate , the purchases are applied to inventory component prepayments that are outstanding with the respective supplier .

**Original gold annotations:**

```json
{
  "table_2": "2016 the 2018 of $ 772 is 744 ;",
  "table_6": "2016 the total of $ 772 is $ 6271 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 029. [train] `IP/2013/page_64.pdf-3`

**Question:** what was the printing papers profit margin in 2011

**Mapped positives:**

- `table-row-1` (table[1]): sales | 2013: $ 3435 | 2012: $ 3170 | 2011: $ 3710
- `table-row-2` (table[2]): operating profit | 2013: 161 | 2012: 268 | 2011: 163

**Five negative candidates:**

- `post-text-15` (post_text[15]): planned maintenance downtime costs should be $ 8 million lower with a planned maintenance outage scheduled at the augusta mill in the first quarter .
- `pre-text-8` (pre_text[8]): planned maintenance downtime costs should be about $ 11 million higher than in the fourth quarter of 2013 .
- `pre-text-12` (pre_text[12]): consumer packaging net sales in 2013 increased 8% ( 8 % ) from 2012 , but decreased 7% ( 7 % ) from 2011 .
- `post-text-6` (post_text[6]): market-related downtime was about 24000 tons in 2013 compared with about 113000 tons in 2012 .
- `post-text-4` (post_text[4]): input costs for wood and energy increased , but were partially offset by lower costs for chemicals .

**Original gold annotations:**

```json
{
  "table_1": "in millions the sales of 2013 is $ 3435 ; the sales of 2012 is $ 3170 ; the sales of 2011 is $ 3710 ;",
  "table_2": "in millions the operating profit of 2013 is 161 ; the operating profit of 2012 is 268 ; the operating profit of 2011 is 163 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 030. [train] `CB/2008/page_216.pdf-2`

**Question:** what is the percentage change in risk-free interest rate from 2007 to 2008?

**Mapped positives:**

- `table-row-3` (table[3]): risk-free interest rate | 2008: 3.15% ( 3.15 % ) | 2007: 4.51% ( 4.51 % ) | 2006: 4.60% ( 4.60 % )

**Five negative candidates:**

- `table-row-2` (table[2]): expected volatility | 2008: 32.20% ( 32.20 % ) | 2007: 27.43% ( 27.43 % ) | 2006: 31.29% ( 31.29 % )
- `table-row-5` (table[5]): expected life | 2008: 5.7 years | 2007: 5.6 years | 2006: 6 years
- `pre-text-1` (pre_text[1]): for the years ended december 31 , 2008 , 2007 and 2006 , the expense for the restricted stock was $ 101 million ( $ 71 million after tax ) , $ 77 million ( $ 57 million after tax ) , and $ 65 million ( $ 49 million after tax ) , respectively .
- `pre-text-11` (pre_text[11]): as of december 31 , 2008 , a total of 989812 common shares remain available for issuance under the espp .
- `pre-text-6` (pre_text[6]): during the company 2019s 2008 annual general meeting , shareholders voted to increase the number of common shares authorized to be issued under the 2004 ltip from 15000000 common shares to 19000000 common shares .

**Original gold annotations:**

```json
{
  "table_3": "the risk-free interest rate of 2008 is 3.15% ( 3.15 % ) ; the risk-free interest rate of 2007 is 4.51% ( 4.51 % ) ; the risk-free interest rate of 2006 is 4.60% ( 4.60 % ) ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 031. [train] `IP/2013/page_64.pdf-1`

**Question:** in 2013 what percentage of consumer packaging sales is attributable to north american consumer packaging net sales?

**Mapped positives:**

- `table-row-1` (table[1]): sales | 2013: $ 3435 | 2012: $ 3170 | 2011: $ 3710
- `post-text-0` (post_text[0]): north american consumer packaging net sales were $ 2.0 billion in 2013 compared with $ 2.0 billion in 2012 and $ 2.5 billion in 2011 .

**Five negative candidates:**

- `pre-text-16` (pre_text[16]): benefits from higher sales volumes ( $ 45 million ) were offset by lower average sales price realizations and an unfavorable mix ( $ 50 million ) , higher operating costs including incremental costs resulting from the shutdown of a paper machine at our augusta , georgia mill ( $ 46 million ) and higher input costs ( $ 6 million ) .
- `pre-text-7` (pre_text[7]): input costs should be flat .
- `pre-text-6` (pre_text[6]): average sales price realizations are expected to improve , reflecting the further realization of previously announced sales price increases for softwood pulp and fluff pulp .
- `post-text-16` (post_text[16]): the severe winter weather in the first quarter of 2014 will negatively impact operating profits .
- `pre-text-9` (pre_text[9]): operating profits will also be negatively impacted by the severe winter weather in the first quarter of 2014 .

**Original gold annotations:**

```json
{
  "table_1": "in millions the sales of 2013 is $ 3435 ; the sales of 2012 is $ 3170 ; the sales of 2011 is $ 3710 ;",
  "text_20": "north american consumer packaging net sales were $ 2.0 billion in 2013 compared with $ 2.0 billion in 2012 and $ 2.5 billion in 2011 ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 032. [train] `C/2018/page_200.pdf-3`

**Question:** in 2018 what was the ratio of the total brokerage payables to total brokerage receivables

**Mapped positives:**

- `table-row-6` (table[6]): total brokerage payables ( 1 ) | december 31 , 2018: $ 64571 | december 31 , 2017: $ 61342
- `table-row-3` (table[3]): total brokerage receivables ( 1 ) | december 31 , 2018: $ 35450 | december 31 , 2017: $ 38384

**Five negative candidates:**

- `table-row-5` (table[5]): payables to brokers dealers and clearing organizations | december 31 , 2018: 24298 | december 31 , 2017: 22601
- `pre-text-3` (pre_text[3]): credit risk is reduced to the extent that an exchange or clearing organization acts as a counterparty to the transaction and replaces the broker , dealer or customer in question .
- `table-row-1` (table[1]): receivables from customers | december 31 , 2018: $ 14415 | december 31 , 2017: $ 19215
- `pre-text-7` (pre_text[7]): exposure to credit risk is impacted by market volatility , which may impair the ability of clients to satisfy their obligations to citi .
- `pre-text-6` (pre_text[6]): where customers cannot meet collateral requirements , citi may liquidate sufficient underlying financial instruments to bring the customer into compliance with the required margin level .

**Original gold annotations:**

```json
{
  "table_6": "in millions of dollars the total brokerage payables ( 1 ) of december 31 , 2018 is $ 64571 ; the total brokerage payables ( 1 ) of december 31 , 2017 is $ 61342 ;",
  "table_3": "in millions of dollars the total brokerage receivables ( 1 ) of december 31 , 2018 is $ 35450 ; the total brokerage receivables ( 1 ) of december 31 , 2017 is $ 38384 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 033. [train] `TFX/2014/page_74.pdf-2`

**Question:** what portion of the total number of securities approved by the security holders remains available for future issuance?

**Mapped positives:**

- `table-row-1` (table[1]): equity compensation plans approved by security holders | number of securitiesto be issued uponexercise ofoutstanding options warrants and rights ( a ) ( b ): 1233672 | weighted-averageexercise price ofoutstanding options warrants and rights: $ 75.93 | number of securitiesremaining available forfuture issuance underequity compensationplans ( excludingsecurities reflected in column ( a ) ) ( c ): 4903018

**Five negative candidates:**

- `post-text-8` (post_text[8]): the following table sets forth certain information as of december 31 , 2014 regarding our equity plans : plan category number of securities to be issued upon exercise of outstanding options , warrants and rights weighted-average exercise price of outstanding options , warrants and rights number of securities remaining available for future issuance under equity compensation plans ( excluding securities reflected in column ( a ) ( b ) ( c ) equity compensation plans approved by security holders 1233672 $ 75.93 4903018 item 13 .
- `post-text-1` (post_text[1]): directors , executive officers and corporate governance for the information required by this item 10 , other than information with respect to our executive officers contained at the end of item 1 of this report , see 201celection of directors , 201d 201cnominees for election to the board of directors , 201d 201ccorporate governance 201d and 201csection 16 ( a ) beneficial ownership reporting compliance , 201d in the proxy statement for our 2015 annual meeting , which information is incorporated herein by reference .
- `pre-text-8` (pre_text[8]): the following table sets forth certain information as of december 31 , 2014 regarding our equity plans : plan category number of securities to be issued upon exercise of outstanding options , warrants and rights weighted-average exercise price of outstanding options , warrants and rights number of securities remaining available for future issuance under equity compensation plans ( excluding securities reflected in column ( a ) ( b ) ( c ) equity compensation plans approved by security holders 1233672 $ 75.93 4903018 item 13 .
- `pre-text-1` (pre_text[1]): directors , executive officers and corporate governance for the information required by this item 10 , other than information with respect to our executive officers contained at the end of item 1 of this report , see 201celection of directors , 201d 201cnominees for election to the board of directors , 201d 201ccorporate governance 201d and 201csection 16 ( a ) beneficial ownership reporting compliance , 201d in the proxy statement for our 2015 annual meeting , which information is incorporated herein by reference .
- `pre-text-0` (pre_text[0]): part iii item 10 .

**Original gold annotations:**

```json
{
  "table_1": "plan category the equity compensation plans approved by security holders of number of securitiesto be issued uponexercise ofoutstanding options warrants and rights ( a ) ( b ) is 1233672 ; the equity compensation plans approved by security holders of weighted-averageexercise price ofoutstanding options warrants and rights is $ 75.93 ; the equity compensation plans approved by security holders of number of securitiesremaining available forfuture issuance underequity compensationplans ( excludingsecurities reflected in column ( a ) ) ( c ) is 4903018 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 034. [train] `RCL/2011/page_16.pdf-2`

**Question:** what was the percentage increase in the global guests from 2007 to 2011

**Mapped positives:**

- `table-row-1` (table[1]): 2007 | global cruiseguests ( 1 ): 16586000 | weighted-averagesupplyofberthsmarketedglobally ( 1 ): 327000 | northamericancruiseguests ( 2 ): 10247000 | weighted-average supply ofberths marketedin northamerica ( 1 ): 212000 | europeancruiseguests: 4080000 | weighted-averagesupply ofberthsmarketed ineurope ( 1 ): 105000
- `table-row-5` (table[5]): 2011 | global cruiseguests ( 1 ): 20227000 | weighted-averagesupplyofberthsmarketedglobally ( 1 ): 412000 | northamericancruiseguests ( 2 ): 11625000 | weighted-average supply ofberths marketedin northamerica ( 1 ): 245000 | europeancruiseguests: 5894000 | weighted-averagesupply ofberthsmarketed ineurope ( 1 ): 149000

**Five negative candidates:**

- `post-text-6` (post_text[6]): other markets in addition to expected industry growth in north america and europe as discussed above , we expect the asia/pacific region to demonstrate an even higher growth rate in the near term , although it will continue to represent a relatively small sector compared to north america and europe .
- `table-row-3` (table[3]): 2009 | global cruiseguests ( 1 ): 17340000 | weighted-averagesupplyofberthsmarketedglobally ( 1 ): 363000 | northamericancruiseguests ( 2 ): 10198000 | weighted-average supply ofberths marketedin northamerica ( 1 ): 222000 | europeancruiseguests: 5000000 | weighted-averagesupply ofberthsmarketed ineurope ( 1 ): 131000
- `post-text-0` (post_text[0]): ( 1 ) source : our estimates of the number of global cruise guests , and the weighted-average supply of berths marketed globally , in north america and europe are based on a combination of data that we obtain from various publicly available cruise industry trade information sources including seatrade insider and cruise line international association .
- `post-text-1` (post_text[1]): in addition , our estimates incorporate our own statistical analysis utilizing the same publicly available cruise industry data as a base .
- `pre-text-5` (pre_text[5]): there are approximately 10 ships with an estimated 28000 berths that are expected to be placed in service in the european cruise market between 2012 and 2016 .

**Original gold annotations:**

```json
{
  "table_1": "year the 2007 of global cruiseguests ( 1 ) is 16586000 ; the 2007 of weighted-averagesupplyofberthsmarketedglobally ( 1 ) is 327000 ; the 2007 of northamericancruiseguests ( 2 ) is 10247000 ; the 2007 of weighted-average supply ofberths marketedin northamerica ( 1 ) is 212000 ; the 2007 of europeancruiseguests is 4080000 ; the 2007 of weighted-averagesupply ofberthsmarketed ineurope ( 1 ) is 105000 ;",
  "table_5": "year the 2011 of global cruiseguests ( 1 ) is 20227000 ; the 2011 of weighted-averagesupplyofberthsmarketedglobally ( 1 ) is 412000 ; the 2011 of northamericancruiseguests ( 2 ) is 11625000 ; the 2011 of weighted-average supply ofberths marketedin northamerica ( 1 ) is 245000 ; the 2011 of europeancruiseguests is 5894000 ; the 2011 of weighted-averagesupply ofberthsmarketed ineurope ( 1 ) is 149000 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 035. [train] `GS/2013/page_167.pdf-4`

**Question:** what percent of financial assets securitized in 2012 were residential mortgages?

**Mapped positives:**

- `table-row-1` (table[1]): residential mortgages | year ended december 2013: $ 29772 | year ended december 2012: $ 33755 | year ended december 2011: $ 40131
- `table-row-4` (table[4]): total | year ended december 2013: $ 35858 | year ended december 2012: $ 34055 | year ended december 2011: $ 40400

**Five negative candidates:**

- `pre-text-9` (pre_text[9]): for transfers of assets that are not accounted for as sales , the assets remain in 201cfinancial instruments owned , at fair value 201d and the transfer is accounted for as a collateralized financing , with the related interest expense recognized over the life of the transaction .
- `pre-text-13` (pre_text[13]): the primary risks included in beneficial interests and other interests from the firm 2019s continuing involvement with securitization vehicles are the performance of the underlying collateral , the position of the firm 2019s investment in the capital structure of the securitization vehicle and the market yield for the security .
- `post-text-0` (post_text[0]): goldman sachs 2013 annual report 165 .
- `table-row-5` (table[5]): cash flows on retained interests | year ended december 2013: $ 249 | year ended december 2012: $ 389 | year ended december 2011: $ 569
- `pre-text-15` (pre_text[15]): see notes 5 through 8 for further information about fair value measurements .

**Original gold annotations:**

```json
{
  "table_1": "in millions the residential mortgages of year ended december 2013 is $ 29772 ; the residential mortgages of year ended december 2012 is $ 33755 ; the residential mortgages of year ended december 2011 is $ 40131 ;",
  "table_4": "in millions the total of year ended december 2013 is $ 35858 ; the total of year ended december 2012 is $ 34055 ; the total of year ended december 2011 is $ 40400 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 036. [dev] `C/2017/page_328.pdf-2`

**Question:** as of 2017 what was the ratio of the overall five-year cumulative total return for s&p 500 compared to citi

**Mapped positives:**

- `table-row-6` (table[6]): 31-dec-2017 | citi: 193.5 | s&p 500: 208.1 | s&p financials: 230.9

**Five negative candidates:**

- `table-row-3` (table[3]): 31-dec-2014 | citi: 137.0 | s&p 500: 150.5 | s&p financials: 156.2
- `table-row-4` (table[4]): 31-dec-2015 | citi: 131.4 | s&p 500: 152.6 | s&p financials: 153.9
- `table-row-1` (table[1]): 31-dec-2012 | citi: 100.0 | s&p 500: 100.0 | s&p financials: 100.0
- `table-row-2` (table[2]): 31-dec-2013 | citi: 131.8 | s&p 500: 132.4 | s&p financials: 135.6
- `post-text-0` (post_text[0]): .

**Original gold annotations:**

```json
{
  "table_6": "date the 31-dec-2017 of citi is 193.5 ; the 31-dec-2017 of s&p 500 is 208.1 ; the 31-dec-2017 of s&p financials is 230.9 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 037. [train] `ETR/2009/page_107.pdf-2`

**Question:** what portion of the securitization bonds issued by entergy gulf states reconstruction funding has a maturity date in 2022?

**Mapped positives:**

- `table-row-4` (table[4]): tranche a-3 ( 5.93% ( 5.93 % ) ) due june 2022 | amount ( in thousands ): 114400
- `table-row-5` (table[5]): total senior secured transition bonds | amount ( in thousands ): $ 329500
- `pre-text-8` (pre_text[8]): if entergy's debt ratio exceeds this limit , or if entergy corporation or certain of the utility operating companies default on other indebtedness or are in bankruptcy or insolvency proceedings , an acceleration of the notes' maturity dates may occur .

**Five negative candidates:**

- `pre-text-2` (pre_text[2]): these notes do not have a stated interest rate , but have an implicit interest rate of 4.8% ( 4.8 % ) .
- `pre-text-5` (pre_text[5]): in july 2003 , a payment of $ 102 million was made prior to maturity on the note payable to nypa .
- `pre-text-7` (pre_text[7]): covenants in the entergy corporation notes require it to maintain a consolidated debt ratio of 65% ( 65 % ) or less of its total capitalization .
- `table-row-2` (table[2]): tranche a-1 ( 5.51% ( 5.51 % ) ) due october 2013 | amount ( in thousands ): $ 93500
- `table-row-1` (table[1]): senior secured transition bonds series a: | amount ( in thousands ):

**Original gold annotations:**

```json
{
  "table_4": "the tranche a-3 ( 5.93% ( 5.93 % ) ) due june 2022 of amount ( in thousands ) is 114400 ;",
  "table_5": "the total senior secured transition bonds of amount ( in thousands ) is $ 329500 ;",
  "text_8": "if entergy's debt ratio exceeds this limit , or if entergy corporation or certain of the utility operating companies default on other indebtedness or are in bankruptcy or insolvency proceedings , an acceleration of the notes' maturity dates may occur ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 038. [train] `UNP/2007/page_22.pdf-4`

**Question:** what percentage of the total number of shares purchased were purchased in october?

**Mapped positives:**

- `table-row-1` (table[1]): oct . 1 through oct . 31 | totalnumber ofsharespurchased[a]: 99782 | averagepricepaid pershare: $ 128.78 | total number of sharespurchased as part of apublicly announcedplan orprogram: - | maximum number ofshares that may yetbe purchased underthe plan orprogram[b]: 9774279
- `table-row-4` (table[4]): total | totalnumber ofsharespurchased[a]: 2626154 | averagepricepaid pershare: $ 127.75 | total number of sharespurchased as part of apublicly announcedplan orprogram: 2397800 | maximum number ofshares that may yetbe purchased underthe plan orprogram[b]: n/a

**Five negative candidates:**

- `pre-text-1` (pre_text[1]): the graph assumes that the value of the investment in the common stock of union pacific corporation and each index was $ 100 on december 31 , 2002 , and that all dividends were reinvested .
- `post-text-2` (post_text[2]): we may make these repurchases on the open market or through other transactions .
- `post-text-1` (post_text[1]): [b] on january 30 , 2007 , our board of directors authorized us to repurchase up to 20 million shares of our common stock through december 31 , 2009 .
- `pre-text-3` (pre_text[3]): during the first nine months of 2007 , we repurchased 10639916 shares of our common stock at an average price per share of $ 112.68 .
- `table-row-0` (table[0]): period | totalnumber ofsharespurchased[a] | averagepricepaid pershare | total number of sharespurchased as part of apublicly announcedplan orprogram | maximum number ofshares that may yetbe purchased underthe plan orprogram[b]

**Original gold annotations:**

```json
{
  "table_1": "period the oct . 1 through oct . 31 of totalnumber ofsharespurchased[a] is 99782 ; the oct . 1 through oct . 31 of averagepricepaid pershare is $ 128.78 ; the oct . 1 through oct . 31 of total number of sharespurchased as part of apublicly announcedplan orprogram is - ; the oct . 1 through oct . 31 of maximum number ofshares that may yetbe purchased underthe plan orprogram[b] is 9774279 ;",
  "table_4": "period the total of totalnumber ofsharespurchased[a] is 2626154 ; the total of averagepricepaid pershare is $ 127.75 ; the total of total number of sharespurchased as part of apublicly announcedplan orprogram is 2397800 ; the total of maximum number ofshares that may yetbe purchased underthe plan orprogram[b] is n/a ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 039. [dev] `ETR/2013/page_118.pdf-4`

**Question:** what are the lease obligations to entergy louisiana as a percentage of long-term debt maturities in 2014?

**Mapped positives:**

- `table-row-1` (table[1]): 2014 | amount ( in thousands ): $ 385373
- `pre-text-5` (pre_text[5]): ( e ) the fair value excludes lease obligations of $ 149 million at entergy louisiana and $ 97 million at system energy , long-term doe obligations of $ 181 million at entergy arkansas , and the note payable to nypa of $ 95 million at entergy , and includes debt due within one year .
- `pre-text-7` (pre_text[7]): the annual long-term debt maturities ( excluding lease obligations and long-term doe obligations ) for debt outstanding as of december 31 , 2013 , for the next five years are as follows : amount ( in thousands ) .

**Five negative candidates:**

- `pre-text-3` (pre_text[3]): the contracts include a one-time fee for generation prior to april 7 , 1983 .
- `post-text-7` (post_text[7]): entergy gulf states louisiana , entergy louisiana , entergy mississippi , entergy texas , and system energy have obtained long-term financing authorizations from the ferc that extend through october 2015 .
- `post-text-1` (post_text[1]): entergy issued notes to nypa with seven annual installments of approximately $ 108 million commencing one year from the date of the closing , and eight annual installments of $ 20 million commencing eight years from the date of the closing .
- `pre-text-6` (pre_text[6]): fair values are classified as level 2 in the fair value hierarchy discussed in note 16 to the financial statements and are based on prices derived from inputs such as benchmark yields and reported trades .
- `post-text-10` (post_text[10]): capital funds agreement pursuant to an agreement with certain creditors , entergy corporation has agreed to supply system energy with sufficient capital to : 2022 maintain system energy 2019s equity capital at a minimum of 35% ( 35 % ) of its total capitalization ( excluding short- term debt ) ; .

**Original gold annotations:**

```json
{
  "table_1": "the 2014 of amount ( in thousands ) is $ 385373 ;",
  "text_5": "( e ) the fair value excludes lease obligations of $ 149 million at entergy louisiana and $ 97 million at system energy , long-term doe obligations of $ 181 million at entergy arkansas , and the note payable to nypa of $ 95 million at entergy , and includes debt due within one year .",
  "text_7": "the annual long-term debt maturities ( excluding lease obligations and long-term doe obligations ) for debt outstanding as of december 31 , 2013 , for the next five years are as follows : amount ( in thousands ) ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 040. [train] `SNA/2012/page_54.pdf-1`

**Question:** what is the percentage change in working capital in 2012 relative to 2011?

**Mapped positives:**

- `pre-text-7` (pre_text[7]): as of 2012 year end , working capital ( current assets less current liabilities ) of $ 1079.8 million increased $ 132.9 million from $ 946.9 million at 2011 year end .

**Five negative candidates:**

- `post-text-4` (post_text[4]): snap-on considers these non-u.s .
- `post-text-11` (post_text[11]): 44 snap-on incorporated .
- `table-row-5` (table[5]): inventories 2013 net | 2012: 404.2 | 2011: 386.4
- `table-row-3` (table[3]): finance receivables 2013 net | 2012: 323.1 | 2011: 277.2
- `table-row-8` (table[8]): notes payable | 2012: -5.2 ( 5.2 ) | 2011: -16.2 ( 16.2 )

**Original gold annotations:**

```json
{
  "text_7": "as of 2012 year end , working capital ( current assets less current liabilities ) of $ 1079.8 million increased $ 132.9 million from $ 946.9 million at 2011 year end ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 041. [train] `BKR/2018/page_61.pdf-3`

**Question:** what portion of total contractual obligations is expected to be paid as interest payments?

**Mapped positives:**

- `table-row-2` (table[2]): estimated interest payments ( 2 ) | payments due by period total: 3716 | payments due by period less than1 year: 239 | payments due by period 1 - 3years: 473 | payments due by period 4 - 5years: 404 | payments due by period more than5 years: 2600
- `table-row-5` (table[5]): total | payments due by period total: $ 13058 | payments due by period less than1 year: $ 2755 | payments due by period 1 - 3years: $ 1383 | payments due by period 4 - 5years: $ 1833 | payments due by period more than5 years: $ 7087

**Five negative candidates:**

- `post-text-13` (post_text[13]): we have certain defined benefit pension and other post-retirement benefit plans covering certain of our u.s .
- `post-text-20` (post_text[20]): it is not practicable to estimate the fair value of these financial instruments .
- `post-text-14` (post_text[14]): and international employees .
- `post-text-19` (post_text[19]): off-balance sheet arrangements in the normal course of business with customers , vendors and others , we have entered into off-balance sheet arrangements , such as surety bonds for performance , letters of credit and other bank issued guarantees , which totaled approximately $ 3.6 billion at december 31 , 2018 .
- `post-text-12` (post_text[12]): income taxes" of the notes to consolidated and combined financial statements in item 8 herein for further information .

**Original gold annotations:**

```json
{
  "table_2": "( in millions ) the estimated interest payments ( 2 ) of payments due by period total is 3716 ; the estimated interest payments ( 2 ) of payments due by period less than1 year is 239 ; the estimated interest payments ( 2 ) of payments due by period 1 - 3years is 473 ; the estimated interest payments ( 2 ) of payments due by period 4 - 5years is 404 ; the estimated interest payments ( 2 ) of payments due by period more than5 years is 2600 ;",
  "table_5": "( in millions ) the total of payments due by period total is $ 13058 ; the total of payments due by period less than1 year is $ 2755 ; the total of payments due by period 1 - 3years is $ 1383 ; the total of payments due by period 4 - 5years is $ 1833 ; the total of payments due by period more than5 years is $ 7087 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 042. [train] `HII/2013/page_116.pdf-4`

**Question:** what were the total net earnings year ended december 31 2013 in millions

**Mapped positives:**

- `table-row-4` (table[4]): net earnings ( loss ) | year ended december 31 2013 1st qtr: 44 | year ended december 31 2013 2nd qtr: 57 | year ended december 31 2013 3rd qtr: 69 | year ended december 31 2013 4th qtr: 91

**Five negative candidates:**

- `post-text-0` (post_text[0]): .
- `pre-text-15` (pre_text[15]): unaudited selected quarterly data unaudited quarterly financial results for the years ended december 31 , 2013 and 2012 , are set forth in the following tables: .
- `pre-text-8` (pre_text[8]): management believes that the methods of allocating these costs are reasonable , consistent with past practices , and in conformity with cost allocation requirements of cas or the far .
- `pre-text-1` (pre_text[1]): the consolidated financial statements include northrop grumman management and support services allocations totaling $ 32 million for the year ended december 31 , 2011 .
- `pre-text-2` (pre_text[2]): shared services and infrastructure costs - this category includes costs for functions such as information technology support , systems maintenance , telecommunications , procurement and other shared services while hii was a subsidiary of northrop grumman .

**Original gold annotations:**

```json
{
  "table_4": "( $ in millions except per share amounts ) the net earnings ( loss ) of year ended december 31 2013 1st qtr is 44 ; the net earnings ( loss ) of year ended december 31 2013 2nd qtr is 57 ; the net earnings ( loss ) of year ended december 31 2013 3rd qtr is 69 ; the net earnings ( loss ) of year ended december 31 2013 4th qtr is 91 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 043. [train] `AAPL/2004/page_83.pdf-1`

**Question:** what percentage of the purchase price was spent on goodwill?

**Mapped positives:**

- `table-row-4` (table[4]): goodwill | $ 2.3: 18.6
- `table-row-5` (table[5]): total consideration | $ 2.3: $ 26.0

**Five negative candidates:**

- `pre-text-2` (pre_text[2]): the acquisition has been accounted for as a purchase .
- `table-row-1` (table[1]): acquired technology | $ 2.3: 3.8
- `table-row-3` (table[3]): in-process research and development | $ 2.3: 0.5
- `post-text-0` (post_text[0]): the amount of the purchase price allocated to ipr&d was expensed upon acquisition , because the technological feasibility of products under development had not been established and no alternative future uses existed .
- `post-text-5` (post_text[5]): acquisition of certain assets of zayante , inc. , prismo graphics , and silicon grail during fiscal 2002 the company acquired certain technology and patent rights of zayante , inc. , prismo graphics , and silicon grail corporation for a total of $ 20 million in cash .

**Original gold annotations:**

```json
{
  "table_4": "net tangible assets acquired the goodwill of $ 2.3 is 18.6 ;",
  "table_5": "net tangible assets acquired the total consideration of $ 2.3 is $ 26.0 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 044. [train] `PNC/2011/page_183.pdf-2`

**Question:** were there more isos granted in the year than restricted stock units?

**Mapped positives:**

- `table-row-1` (table[1]): granted | nonvested incentive/ performance unit shares 363: 623 | weighted- average grant date fair value $ 56.40: 64.21 | nonvested restricted stock/ unit shares 2250: 1059 | weighted- average grant date fair value $ 49.95: 62.68

**Five negative candidates:**

- `post-text-3` (post_text[3]): the total fair value of incentive/performance unit share and restricted stock/unit awards vested during 2011 , 2010 and 2009 was approximately $ 52 million , $ 39 million and $ 47 million , respectively .
- `pre-text-3` (pre_text[3]): during 2011 , we issued 731336 shares from treasury stock in connection with stock option exercise activity .
- `pre-text-10` (pre_text[10]): the personnel and compensation committee of the board of directors approves the final award payout with respect to incentive/performance unit share awards .
- `post-text-2` (post_text[2]): this cost is expected to be recognized as expense over a period of no longer than five years .
- `pre-text-0` (pre_text[0]): there were no options granted in excess of market value in 2011 , 2010 or 2009 .

**Original gold annotations:**

```json
{
  "table_1": "shares in thousands december 31 2010 the granted of nonvested incentive/ performance unit shares 363 is 623 ; the granted of weighted- average grant date fair value $ 56.40 is 64.21 ; the granted of nonvested restricted stock/ unit shares 2250 is 1059 ; the granted of weighted- average grant date fair value $ 49.95 is 62.68 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 045. [train] `K/2013/page_27.pdf-2`

**Question:** in 2013 , what percent of net cash from operations is retained as cash flow?

**Mapped positives:**

- `pre-text-5` (pre_text[5]): our cash flow metric is reconciled to the most comparable gaap measure , as follows: .
- `table-row-3` (table[3]): cash flow | 2013: $ 1170 | 2012: $ 1225 | 2011: $ 1001
- `table-row-1` (table[1]): net cash provided by operating activities | 2013: $ 1807 | 2012: $ 1758 | 2011: $ 1595

**Five negative candidates:**

- `post-text-11` (post_text[11]): dollar notes , resulting in aggregate net proceeds after debt discount of $ 645 million .
- `post-text-28` (post_text[28]): in november 2011 , we issued $ 500 million of five-year 1.875% ( 1.875 % ) fixed rate u .
- `table-row-4` (table[4]): year-over-year change | 2013: ( 4.5 ) % (  % ) | 2012: 22.4% ( 22.4 % ) | 2011:
- `post-text-22` (post_text[22]): in december 2012 , we repaid $ 750 million five-year 5.125% ( 5.125 % ) u.s .
- `post-text-8` (post_text[8]): total debt was $ 7.4 billion at year-end 2013 and $ 7.9 billion at year-end 2012 .

**Original gold annotations:**

```json
{
  "text_5": "our cash flow metric is reconciled to the most comparable gaap measure , as follows: .",
  "table_3": "( dollars in millions ) the cash flow of 2013 is $ 1170 ; the cash flow of 2012 is $ 1225 ; the cash flow of 2011 is $ 1001 ;",
  "table_1": "( dollars in millions ) the net cash provided by operating activities of 2013 is $ 1807 ; the net cash provided by operating activities of 2012 is $ 1758 ; the net cash provided by operating activities of 2011 is $ 1595 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 046. [train] `TSCO/2017/page_73.pdf-1`

**Question:** what percent of the 2017 end goodwill balance is the goodwill from the acquisition?

**Mapped positives:**

- `pre-text-1` (pre_text[1]): the changes in the carrying amount of goodwill for the years ended december 30 , 2017 and december 31 , 2016 are as follows ( in thousands ) : .
- `table-row-2` (table[2]): goodwill acquired as part of acquisition | 2017: 2014 | 2016: 84159
- `table-row-5` (table[5]): balance end of year | 2017: $ 93192 | 2016: $ 94417

**Five negative candidates:**

- `post-text-1` (post_text[1]): goodwill is not amortized , but is evaluated for impairment annually and whenever events or changes in circumstances indicate the carrying value of goodwill may not be recoverable .
- `table-row-1` (table[1]): balance beginning of year | 2017: $ 94417 | 2016: $ 10258
- `post-text-6` (post_text[6]): the company determined that the fair value of each reporting unit ( including goodwill ) was in excess of the carrying value of the respective reporting unit .
- `post-text-7` (post_text[7]): in reaching this conclusion , the fair value of each reporting unit was determined based on either a market or an income approach .
- `post-text-9` (post_text[9]): other intangible assets the company had approximately $ 31.3 million of intangible assets other than goodwill at december 30 , 2017 and december 31 , 2016 .

**Original gold annotations:**

```json
{
  "text_1": "the changes in the carrying amount of goodwill for the years ended december 30 , 2017 and december 31 , 2016 are as follows ( in thousands ) : .",
  "table_2": "the goodwill acquired as part of acquisition of 2017 is 2014 ; the goodwill acquired as part of acquisition of 2016 is 84159 ;",
  "table_5": "the balance end of year of 2017 is $ 93192 ; the balance end of year of 2016 is $ 94417 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 047. [dev] `AMAT/2013/page_18.pdf-2`

**Question:** what is the applied 2019s net sales in 2018 , ( in billions ) ?

**Mapped positives:**

- `post-text-15` (post_text[15]): applied 2019s investments in rd&e for product development and engineering programs to create or improve products and technologies over the last three years were as follows : $ 1.3 billion ( 18 percent of net sales ) in fiscal 2013 , $ 1.2 billion ( 14 percent of net sales ) in fiscal 2012 , and $ 1.1 billion ( 11 percent of net sales ) in fiscal 2011 .

**Five negative candidates:**

- `post-text-12` (post_text[12]): product development and engineering organizations are located primarily in the united states , as well as in europe , israel , taiwan , and china .
- `post-text-9` (post_text[9]): research , development and engineering applied 2019s long-term growth strategy requires continued development of new products .
- `post-text-4` (post_text[4]): applied has implemented a distributed manufacturing model under which manufacturing and supply chain activities are conducted in various countries , including the united states , europe , israel , singapore , taiwan , and other countries in asia , and assembly of some systems is completed at customer sites .
- `post-text-1` (post_text[1]): customers may delay delivery of products or cancel orders prior to shipment , subject to possible cancellation penalties .
- `table-row-0` (table[0]): | 2013 | 2012 |  | ( in millions except percentages )

**Original gold annotations:**

```json
{
  "text_18": "applied 2019s investments in rd&e for product development and engineering programs to create or improve products and technologies over the last three years were as follows : $ 1.3 billion ( 18 percent of net sales ) in fiscal 2013 , $ 1.2 billion ( 14 percent of net sales ) in fiscal 2012 , and $ 1.1 billion ( 11 percent of net sales ) in fiscal 2011 ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 048. [train] `GS/2017/page_104.pdf-4`

**Question:** what was the percentage change in average daily var in the currency rates risk category between 2016 and 2017?

**Mapped positives:**

- `table-row-3` (table[3]): currency rates | year ended december 2017: 12 | year ended december 2016: 21 | year ended december 2015: 30

**Five negative candidates:**

- `pre-text-3` (pre_text[3]): the purpose of the firmwide limits is to assist senior management in controlling our overall risk profile .
- `table-row-5` (table[5]): diversification effect | year ended december 2017: -35 ( 35 ) | year ended december 2016: -45 ( 45 ) | year ended december 2015: -47 ( 47 )
- `pre-text-10` (pre_text[10]): such instances are remediated by an inventory reduction and/or a temporary or permanent increase to the risk limit .
- `pre-text-5` (pre_text[5]): sub-limits set the desired maximum amount of exposure that may be managed by any particular business on a day-to-day basis without additional levels of senior management approval , effectively leaving day-to-day decisions to individual desk managers and traders .
- `pre-text-11` (pre_text[11]): model review and validation our var and stress testing models are regularly reviewed by market risk management and enhanced in order to incorporate changes in the composition of positions included in our market risk measures , as well as variations in market conditions .

**Original gold annotations:**

```json
{
  "table_3": "$ in millions the currency rates of year ended december 2017 is 12 ; the currency rates of year ended december 2016 is 21 ; the currency rates of year ended december 2015 is 30 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 049. [train] `C/2015/page_314.pdf-4`

**Question:** what was the overall percentage growth of the cumulative total return for citi from 2010 to 2015

**Mapped positives:**

- `table-row-1` (table[1]): 31-dec-2010 | citi: 100.00 | s&p 500: 100.00 | s&p financials: 100.00
- `table-row-6` (table[6]): 31-dec-2015 | citi: 110.14 | s&p 500: 180.75 | s&p financials: 164.39

**Five negative candidates:**

- `table-row-5` (table[5]): 31-dec-2014 | citi: 114.83 | s&p 500: 178.28 | s&p financials: 166.93
- `post-text-0` (post_text[0]): .
- `pre-text-1` (pre_text[1]): the graph and table assume that $ 100 was invested on december 31 , 2010 in citi 2019s common stock , the s&p 500 index and the s&p financial index , and that all dividends were reinvested .
- `pre-text-2` (pre_text[2]): comparison of five-year cumulative total return for the years ended date citi s&p 500 financials .
- `table-row-3` (table[3]): 31-dec-2012 | citi: 83.81 | s&p 500: 118.45 | s&p financials: 106.84

**Original gold annotations:**

```json
{
  "table_1": "date the 31-dec-2010 of citi is 100.00 ; the 31-dec-2010 of s&p 500 is 100.00 ; the 31-dec-2010 of s&p financials is 100.00 ;",
  "table_6": "date the 31-dec-2015 of citi is 110.14 ; the 31-dec-2015 of s&p 500 is 180.75 ; the 31-dec-2015 of s&p financials is 164.39 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 050. [train] `PNC/2013/page_205.pdf-1`

**Question:** what was the total fair value of incentive/performance unit share and restricted stock/unit awards vested during 2013 and 2012 in millions?

**Mapped positives:**

- `pre-text-9` (pre_text[9]): during 2013 , we issued approximately 2.6 million shares from treasury stock in connection with stock option exercise activity .
- `pre-text-25` (pre_text[25]): the total fair value of incentive/performance unit share and restricted stock/unit awards vested during 2013 , 2012 and 2011 was approximately $ 63 million , $ 55 million and $ 52 million , respectively .

**Five negative candidates:**

- `pre-text-18` (pre_text[18]): beginning in 2013 , we incorporated several enhanced risk- related performance changes to certain long-term incentive compensation programs .
- `pre-text-22` (pre_text[22]): additionally , performance-based restricted share units were granted in 2013 to certain executives as part of annual bonus deferral criteria .
- `pre-text-7` (pre_text[7]): shares of common stock available during the next year for the granting of options and other awards under the incentive plans were 24535159 at december 31 , 2013 .
- `pre-text-19` (pre_text[19]): in addition to achieving certain financial performance metrics on both an absolute basis and relative to our peers , final payout amounts will be subject to reduction if pnc fails to meet certain risk-related performance metrics as specified in the award agreement .
- `post-text-1` (post_text[1]): 2013 form 10-k 187 .

**Original gold annotations:**

```json
{
  "text_9": "during 2013 , we issued approximately 2.6 million shares from treasury stock in connection with stock option exercise activity .",
  "text_25": "the total fair value of incentive/performance unit share and restricted stock/unit awards vested during 2013 , 2012 and 2011 was approximately $ 63 million , $ 55 million and $ 52 million , respectively ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 051. [train] `ADI/2007/page_82.pdf-1`

**Question:** what is the growth rate in rental expense under operating leases in 2007?

**Mapped positives:**

- `pre-text-5` (pre_text[5]): total rental expense under operating leases was approximately $ 43 million in fiscal 2007 , $ 45 million in fiscal 2006 and $ 44 million in fiscal 2005 .

**Five negative candidates:**

- `post-text-8` (post_text[8]): there can be no assurance a final settlement will be so approved .
- `table-row-4` (table[4]): 2011 | operating leases: $ 5430
- `post-text-11` (post_text[11]): specifically , the issue related to options granted to employees ( including officers ) of the company on november 30 , 1999 and to employees ( including officers ) and directors of the company on november 10 , 2000 .
- `table-row-0` (table[0]): fiscal years | operating leases
- `post-text-3` (post_text[3]): at all times since receiving notice of this inquiry , the company has cooperated with the sec .

**Original gold annotations:**

```json
{
  "text_5": "total rental expense under operating leases was approximately $ 43 million in fiscal 2007 , $ 45 million in fiscal 2006 and $ 44 million in fiscal 2005 ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 052. [train] `PNC/2012/page_46.pdf-3`

**Question:** when pnc redeemed all shares of the series m preferred stock from the trust on december 10 , 2012 , what was the total cash cost of the redemption?

**Mapped positives:**

- `pre-text-9` (pre_text[9]): we include here by reference the information regarding our compensation plans under which pnc equity securities are authorized for issuance as of december 31 , 2012 in the table ( with introductory paragraph and notes ) that appears in item 12 of this report .
- `post-text-3` (post_text[3]): immediately upon such issuance , pnc redeemed all 5001 shares of the series m preferred stock from the trust on december 10 , 2012 at a redemption price equal to $ 100000 per share .

**Five negative candidates:**

- `table-row-4` (table[4]): total | total sharespurchased ( b ): 1055 | averagepricepaid pershare: $ 55.32 | total sharespurchased aspartofpubliclyannouncedprograms ( c ): 1001 | maximumnumber ofshares thatmay yet bepurchasedundertheprograms ( c ):
- `post-text-10` (post_text[10]): 2013 form 10-k 27 .
- `pre-text-8` (pre_text[8]): we include here by reference additional information relating to pnc common stock under the caption 201ccommon stock prices/dividends declared 201d in the statistical information ( unaudited ) section of item 8 of this report .
- `post-text-2` (post_text[2]): on december 10 , 2012 , pnc issued $ 500.1 million aggregate liquidation amount ( 5001 shares ) of the series m preferred stock to the national city preferred capital trust i ( the 201ctrust 201d ) as required pursuant to the settlement of a stock purchase contract agreement between the trust and pnc dated as of january 30 , 2008 .
- `table-row-0` (table[0]): 2012 period ( a ) | total sharespurchased ( b ) | averagepricepaid pershare | total sharespurchased aspartofpubliclyannouncedprograms ( c ) | maximumnumber ofshares thatmay yet bepurchasedundertheprograms ( c )

**Original gold annotations:**

```json
{
  "text_9": "we include here by reference the information regarding our compensation plans under which pnc equity securities are authorized for issuance as of december 31 , 2012 in the table ( with introductory paragraph and notes ) that appears in item 12 of this report .",
  "text_18": "immediately upon such issuance , pnc redeemed all 5001 shares of the series m preferred stock from the trust on december 10 , 2012 at a redemption price equal to $ 100000 per share ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 053. [train] `ETR/2013/page_136.pdf-2`

**Question:** what portion of the total future minimum lease payments for system energy is due in the next 12 months?

**Mapped positives:**

- `table-row-1` (table[1]): 2014 | amount ( in thousands ): $ 51637
- `table-row-7` (table[7]): total | amount ( in thousands ): 392640

**Five negative candidates:**

- `post-text-0` (post_text[0]): .
- `table-row-8` (table[8]): less : amount representing interest | amount ( in thousands ): 295226
- `table-row-2` (table[2]): 2015 | amount ( in thousands ): 52253
- `table-row-9` (table[9]): present value of net minimum lease payments | amount ( in thousands ): $ 97414
- `table-row-0` (table[0]): | amount ( in thousands )

**Original gold annotations:**

```json
{
  "table_1": "the 2014 of amount ( in thousands ) is $ 51637 ;",
  "table_7": "the total of amount ( in thousands ) is 392640 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 054. [dev] `FBHS/2017/page_76.pdf-2`

**Question:** what was the percentage growth in the total long-term debt from 2016 to 2017

**Mapped positives:**

- `table-row-6` (table[6]): total long-term debt | 2017: $ 1507.6 | 2016: $ 1431.1

**Five negative candidates:**

- `table-row-2` (table[2]): $ 500 million unsecured senior note due june 2025 | 2017: 494.3 | 2016: 493.5
- `table-row-0` (table[0]): ( in millions ) | 2017 | 2016
- `post-text-15` (post_text[15]): there were no material commodity swap contracts outstanding for the years ended december 31 , 2017 and 2016 .
- `post-text-14` (post_text[14]): changes in the fair value of economic hedges are recorded directly into current period earnings .
- `post-text-16` (post_text[16]): we enter into foreign exchange contracts primarily to hedge forecasted sales and purchases denominated in select foreign currencies , thereby limiting currency risk that would otherwise result from changes in exchange rates .

**Original gold annotations:**

```json
{
  "table_6": "( in millions ) the total long-term debt of 2017 is $ 1507.6 ; the total long-term debt of 2016 is $ 1431.1 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 055. [train] `HII/2011/page_60.pdf-2`

**Question:** what is the percentage change in the weighted average discount rate for other post-retirement benefits from 2010 to 2011?

**Mapped positives:**

- `pre-text-7` (pre_text[7]): our weighted average discount rate for other postretirement benefits was 4.94% ( 4.94 % ) and 5.58% ( 5.58 % ) as of december 31 , 2011 and 2010 , respectively .

**Five negative candidates:**

- `pre-text-3` (pre_text[3]): we use only bonds that are denominated in u.s .
- `table-row-4` (table[4]): 25 basis point increase in expected return on assets | increase ( decrease ) in 2012 expense: -8 ( 8 ) | increase ( decrease ) in december 31 2011 obligations: n.a .
- `table-row-2` (table[2]): 25 basis point increase in discount rate | increase ( decrease ) in 2012 expense: -17 ( 17 ) | increase ( decrease ) in december 31 2011 obligations: -154 ( 154 )
- `post-text-5` (post_text[5]): while the ultimate liability for such costs under fas and cas is similar , the pattern of cost recognition is different .
- `pre-text-8` (pre_text[8]): expected long-term rate of return 2014the expected long-term rate of return on assets is used to calculate net periodic expense , and is based on such factors as historical returns , targeted asset allocations , investment policy , duration , expected future long-term performance of individual asset classes , inflation trends , portfolio volatility , and risk management strategies .

**Original gold annotations:**

```json
{
  "text_7": "our weighted average discount rate for other postretirement benefits was 4.94% ( 4.94 % ) and 5.58% ( 5.58 % ) as of december 31 , 2011 and 2010 , respectively ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 056. [train] `HUM/2016/page_133.pdf-1`

**Question:** in 2014 what was the number of shares issued a dividend in millions

**Mapped positives:**

- `table-row-1` (table[1]): 2014 | amountper share: $ 1.10 | totalamount ( in millions ): $ 170

**Five negative candidates:**

- `post-text-2` (post_text[2]): on february 14 , 2017 , following the termination of the merger agreement , the board declared a cash dividend of $ 0.40 per share , to be paid on april 28 , 2017 , to the stockholders of record on march 31 , 2017 .
- `pre-text-3` (pre_text[3]): the adoption of this new guidance resulted in the recognition of approximately $ 20 million of tax benefits in net income in our consolidated statement of income for the three months ended march 31 , 2016 that had previously been recorded as additional paid-in capital in our consolidated balance sheet .
- `pre-text-0` (pre_text[0]): humana inc .
- `post-text-5` (post_text[5]): under the share repurchase authorization , shares may have been purchased from time to time at prevailing prices in the open market , by block purchases , through plans designed to comply with rule 10b5-1 under the securities exchange act of 1934 , as amended , or in privately-negotiated transactions ( including pursuant to accelerated share repurchase agreements with investment banks ) , subject to certain regulatory restrictions on volume , pricing , and timing .
- `table-row-2` (table[2]): 2015 | amountper share: $ 1.14 | totalamount ( in millions ): $ 170

**Original gold annotations:**

```json
{
  "table_1": "paymentdate the 2014 of amountper share is $ 1.10 ; the 2014 of totalamount ( in millions ) is $ 170 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 057. [train] `ZBH/2008/page_84.pdf-4`

**Question:** what was the percentage change in weighted average shares outstanding for diluted net earnings per share from 2006 to 2007?

**Mapped positives:**

- `table-row-3` (table[3]): weighted average shares outstanding for diluted net earnings per share | 2008: 228.3 | 2007: 237.5 | 2006: 245.4

**Five negative candidates:**

- `post-text-3` (post_text[3]): in april 2008 , we announced that our board of directors authorized a $ 1.25 billion share repurchase program which expires december 31 , 2009 .
- `pre-text-4` (pre_text[4]): the most significant foreign tax jurisdiction under examination is the united kingdom .
- `post-text-16` (post_text[16]): z i m m e r h o l d i n g s , i n c .
- `pre-text-6` (pre_text[6]): 13 .
- `pre-text-3` (pre_text[3]): our tax returns are currently under examination in various foreign jurisdictions .

**Original gold annotations:**

```json
{
  "table_3": "the weighted average shares outstanding for diluted net earnings per share of 2008 is 228.3 ; the weighted average shares outstanding for diluted net earnings per share of 2007 is 237.5 ; the weighted average shares outstanding for diluted net earnings per share of 2006 is 245.4 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 058. [dev] `MRO/2017/page_111.pdf-3`

**Question:** what would end of year proven reserves be without the increase for extensions , discoveries , and other additions , in mmboe?

**Mapped positives:**

- `table-row-7` (table[7]): end of year | 552: 546
- `table-row-4` (table[4]): extensions discoveries and other additions | 552: 57

**Five negative candidates:**

- `table-row-2` (table[2]): improved recovery | 552: 2014
- `pre-text-3` (pre_text[3]): 2022 production : decreased by 145 mmboe .
- `pre-text-15` (pre_text[15]): resource plays and an increase of 67 mmboe in discontinued operations due to technical reevaluation and lower royalty percentages related to lower realized prices , offset by a decrease of 173 mmboe which was largely due to reductions to our capital development program and adherence to the sec 5-year rule .
- `pre-text-7` (pre_text[7]): 2016 proved reserves decreased by 67 mmboe primarily due to the following : 2022 revisions of previous estimates : increased by 63 mmboe primarily due to an increase of 151 mmboe associated with the acceleration of higher economic wells in the u.s .
- `pre-text-8` (pre_text[8]): resource plays into the 5-year plan and a decrease of 64 mmboe due to u.s .

**Original gold annotations:**

```json
{
  "table_7": "beginning of year the end of year of 552 is 546 ;",
  "table_4": "beginning of year the extensions discoveries and other additions of 552 is 57 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 059. [train] `GS/2013/page_91.pdf-3`

**Question:** what is the difference in millions , between additional collateral or termination payments for a two-notch downgrade and additional collateral or termination payments for a one-notch downgrade at the end of december 2012?

**Mapped positives:**

- `table-row-1` (table[1]): additional collateral or termination payments for a one-notch downgrade | as of december 2013: $ 911 | as of december 2012: $ 1534
- `table-row-2` (table[2]): additional collateral or termination payments for a two-notch downgrade | as of december 2013: 2989 | as of december 2012: 2500

**Five negative candidates:**

- `post-text-2` (post_text[2]): cash flow analysis may , however , be helpful in highlighting certain macro trends and strategic initiatives in our businesses .
- `pre-text-4` (pre_text[4]): we allocate a portion of our gce to ensure we would be able to make the additional collateral or termination payments that may be required in the event of a two-notch reduction in our long-term credit ratings , as well as collateral that has not been called by counterparties , but is available to them .
- `post-text-1` (post_text[1]): consequently , we believe that traditional cash flow analysis is less meaningful in evaluating our liquidity position than the excess liquidity and asset-liability management policies described above .
- `post-text-11` (post_text[11]): year ended december 2011 .
- `post-text-12` (post_text[12]): our cash and cash equivalents increased by $ 16.22 billion to $ 56.01 billion at the end of 2011 .

**Original gold annotations:**

```json
{
  "table_1": "in millions the additional collateral or termination payments for a one-notch downgrade of as of december 2013 is $ 911 ; the additional collateral or termination payments for a one-notch downgrade of as of december 2012 is $ 1534 ;",
  "table_2": "in millions the additional collateral or termination payments for a two-notch downgrade of as of december 2013 is 2989 ; the additional collateral or termination payments for a two-notch downgrade of as of december 2012 is 2500 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 060. [train] `MO/2016/page_76.pdf-3`

**Question:** what are the total number of pending tobacco-related cases in united states in 2015?

**Mapped positives:**

- `table-row-1` (table[1]): individual smoking and health cases ( 2 ) | 2016: 70 | 2015: 65 | 2014: 67
- `table-row-2` (table[2]): smoking and health class actions and aggregated claims litigation ( 3 ) | 2016: 5 | 2015: 5 | 2014: 5
- `table-row-3` (table[3]): health care cost recovery actions ( 4 ) | 2016: 1 | 2015: 1 | 2014: 1
- `table-row-4` (table[4]): 201clights/ultra lights 201d class actions | 2016: 8 | 2015: 11 | 2014: 12

**Five negative candidates:**

- `post-text-15` (post_text[15]): the first trial is currently scheduled to begin may 1 , 2018 .
- `pre-text-13` (pre_text[13]): altria group , inc .
- `post-text-4` (post_text[4]): also , does not include individual smoking and health cases brought by or on behalf of plaintiffs in florida state and federal courts following the decertification of the engle case ( discussed below in smoking and health litigation - engle class action ) .
- `post-text-2` (post_text[2]): the flight attendants allege that they are members of an ets smoking and health class action in florida , which was settled in 1997 ( broin ) .
- `pre-text-10` (pre_text[10]): at the present time , while it is reasonably possible that an unfavorable outcome in a case may occur , except to the extent discussed elsewhere in this note 19 .

**Original gold annotations:**

```json
{
  "table_1": "the individual smoking and health cases ( 2 ) of 2016 is 70 ; the individual smoking and health cases ( 2 ) of 2015 is 65 ; the individual smoking and health cases ( 2 ) of 2014 is 67 ;",
  "table_2": "the smoking and health class actions and aggregated claims litigation ( 3 ) of 2016 is 5 ; the smoking and health class actions and aggregated claims litigation ( 3 ) of 2015 is 5 ; the smoking and health class actions and aggregated claims litigation ( 3 ) of 2014 is 5 ;",
  "table_3": "the health care cost recovery actions ( 4 ) of 2016 is 1 ; the health care cost recovery actions ( 4 ) of 2015 is 1 ; the health care cost recovery actions ( 4 ) of 2014 is 1 ;",
  "table_4": "the 201clights/ultra lights 201d class actions of 2016 is 8 ; the 201clights/ultra lights 201d class actions of 2015 is 11 ; the 201clights/ultra lights 201d class actions of 2014 is 12 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 061. [train] `HUM/2013/page_52.pdf-4`

**Question:** what is the percentual increase observed in the average price paid per share during november and december of 2013?

**Mapped positives:**

- `table-row-2` (table[2]): november 2013 | total number of shares purchased ( 1 ): 1191867 | average price paid per share: 98.18 | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ): 1191867 | dollar value of shares that may yet be purchased under the plans orprograms ( 1 ): 664123417
- `table-row-3` (table[3]): december 2013 | total number of shares purchased ( 1 ): 802930 | average price paid per share: 104.10 | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ): 802930 | dollar value of shares that may yet be purchased under the plans orprograms ( 1 ): 580555202

**Five negative candidates:**

- `table-row-1` (table[1]): october 2013 | total number of shares purchased ( 1 ): 0 | average price paid per share: $ 0 | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ): 0 | dollar value of shares that may yet be purchased under the plans orprograms ( 1 ): $ 781118739
- `post-text-3` (post_text[3]): ( 2 ) excludes 0.1 million shares repurchased in connection with employee stock plans. .
- `pre-text-0` (pre_text[0]): issuer purchases of equity securities the following table provides information about purchases by us during the three months ended december 31 , 2013 of equity securities that are registered by us pursuant to section 12 of the exchange act : period total number of shares purchased ( 1 ) average price paid per share total number of shares purchased as part of publicly announced plans or programs ( 1 ) ( 2 ) dollar value of shares that may yet be purchased under the plans or programs ( 1 ) .
- `table-row-0` (table[0]): period | total number of shares purchased ( 1 ) | average price paid per share | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ) | dollar value of shares that may yet be purchased under the plans orprograms ( 1 )
- `table-row-4` (table[4]): total | total number of shares purchased ( 1 ): 1994797 | average price paid per share: $ 100.56 | total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ): 1994797 | dollar value of shares that may yet be purchased under the plans orprograms ( 1 ):

**Original gold annotations:**

```json
{
  "table_2": "period the november 2013 of total number of shares purchased ( 1 ) is 1191867 ; the november 2013 of average price paid per share is 98.18 ; the november 2013 of total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ) is 1191867 ; the november 2013 of dollar value of shares that may yet be purchased under the plans orprograms ( 1 ) is 664123417 ;",
  "table_3": "period the december 2013 of total number of shares purchased ( 1 ) is 802930 ; the december 2013 of average price paid per share is 104.10 ; the december 2013 of total number of shares purchased as part of publicly announcedplans or programs ( 1 ) ( 2 ) is 802930 ; the december 2013 of dollar value of shares that may yet be purchased under the plans orprograms ( 1 ) is 580555202 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 062. [train] `LMT/2018/page_86.pdf-2`

**Question:** what is the operating profit margin?

**Mapped positives:**

- `table-row-5` (table[5]): operating profit | $ 3410: 454

**Five negative candidates:**

- `pre-text-4` (pre_text[4]): gaap , as the divestiture of this business represented a strategic shift that had a major effect on our operations and financial results .
- `post-text-6` (post_text[6]): the service portion of net pension costs related to is&gs business 2019s salaried employees that transferred to leidos were included in the operating results of the is&gs business classified as discontinued operations because such costs are no longer incurred by us .
- `pre-text-1` (pre_text[1]): the net gain represents the $ 2.5 billion fair value of the shares of lockheed martin common stock exchanged and retired as part of the exchange offer , plus the $ 1.8 billion one-time special cash payment , less the net book value of the is&gs business of about $ 3.0 billion at august 16 , 2016 and other adjustments of about $ 100 million .
- `post-text-2` (post_text[2]): as a result , we reclassified $ 82 million in 2016 of corporate overhead costs from the is&gs business to other unallocated , net on our consolidated statement of earnings .
- `post-text-4` (post_text[4]): therefore , the non-service portion of net pension costs ( e.g. , interest cost , actuarial gains and losses and expected return on plan assets ) for these plans have been reclassified from the operating results of the is&gs business segment and reported as a reduction to the fas/cas pension adjustment .

**Original gold annotations:**

```json
{
  "table_5": "net sales the operating profit of $ 3410 is 454 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 063. [train] `ADI/2010/page_73.pdf-1`

**Question:** what is the total value of restricted stock units outstanding at october 30 , 2010?

**Mapped positives:**

- `table-row-5` (table[5]): restricted stock units outstanding at october 30 2010 | restricted stock units outstanding: 1265 | weighted- average grant- date fair value per share: $ 28.21

**Five negative candidates:**

- `pre-text-1` (pre_text[1]): the total grant-date fair value of stock options that vested during fiscal 2010 , fiscal 2009 and fiscal 2008 was approximately $ 67.2 million , $ 73.6 million and $ 77.6 million , respectively .
- `post-text-2` (post_text[2]): common stock repurchase program the company 2019s common stock repurchase program has been in place since august 2004 .
- `post-text-13` (post_text[13]): analog devices , inc .
- `pre-text-2` (pre_text[2]): proceeds from stock option exercises pursuant to employee stock plans in the company 2019s statement of cash flows of $ 216.1 million , $ 12.4 million and $ 94.2 million for fiscal 2010 , fiscal 2009 and fiscal 2008 , respectively , are net of the value of shares surrendered by employees in certain limited circumstances to satisfy the exercise price of options , and to satisfy employee tax obligations upon vesting of restricted stock or restricted stock units and in connection with the exercise of stock options granted to the company 2019s employees under the company 2019s equity compensation plans .
- `table-row-3` (table[3]): restrictions lapsed | restricted stock units outstanding: -19 ( 19 ) | weighted- average grant- date fair value per share: $ 24.70

**Original gold annotations:**

```json
{
  "table_5": "the restricted stock units outstanding at october 30 2010 of restricted stock units outstanding is 1265 ; the restricted stock units outstanding at october 30 2010 of weighted- average grant- date fair value per share is $ 28.21 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 064. [train] `ETR/2016/page_424.pdf-3`

**Question:** what is the net change in entergy texas 2019s receivables from the money pool from 2014 to 2015?

**Mapped positives:**

- `table-row-2` (table[2]): $ 681 | 2015: ( $ 22068 ) | 2014: $ 306 | 2013: $ 6287

**Five negative candidates:**

- `pre-text-11` (pre_text[11]): all debt and common and preferred stock issuances by entergy texas require prior regulatory approval .
- `pre-text-2` (pre_text[2]): see 201ccritical accounting estimates - qualified pension and other postretirement benefits 201d below for a discussion of qualified pension and other postretirement benefits funding .
- `pre-text-7` (pre_text[7]): management provides more information on long-term debt in note 5 to the financial statements .
- `pre-text-9` (pre_text[9]): sources of capital entergy texas 2019s sources to meet its capital requirements include : 2022 internally generated funds ; 2022 cash on hand ; 2022 debt or preferred stock issuances ; and 2022 bank financing under new or existing facilities .
- `pre-text-5` (pre_text[5]): in addition to routine capital spending to maintain operations , the planned capital investment estimate for entergy texas includes specific investments such as the montgomery county power station discussed below ; transmission projects to enhance reliability , reduce congestion , and enable economic growth ; distribution spending to enhance reliability and improve service to customers , including initial investment to support advanced metering ; system improvements ; and other investments .

**Original gold annotations:**

```json
{
  "table_2": "2016 the $ 681 of 2015 is ( $ 22068 ) ; the $ 681 of 2014 is $ 306 ; the $ 681 of 2013 is $ 6287 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 065. [train] `CMCSA/2015/page_42.pdf-2`

**Question:** what was the differencet in percentage 5 year cumulative total return for comcast class a stock and the s&p 500 stock index for the year ended 2015?

**Mapped positives:**

- `table-row-1` (table[1]): comcast class a | 2011: $ 110 | 2012: $ 177 | 2013: $ 250 | 2014: $ 282 | 2015: $ 279
- `table-row-2` (table[2]): s&p 500 stock index | 2011: $ 102 | 2012: $ 118 | 2013: $ 156 | 2014: $ 177 | 2015: $ 180
- `pre-text-7` (pre_text[7]): the graph assumes $ 100 was invested on december 31 , 2010 in our class a common stock and in each of the following indices and assumes the reinvestment of dividends .

**Five negative candidates:**

- `pre-text-1` (pre_text[1]): this peer group consists of us , as well as cablevision systems corporation ( class a ) , dish network corporation ( class a ) , directv inc .
- `pre-text-2` (pre_text[2]): ( included through july 24 , 2015 , the date of acquisition by at&t corp. ) and time warner cable inc .
- `table-row-0` (table[0]): | 2011 | 2012 | 2013 | 2014 | 2015
- `pre-text-6` (pre_text[6]): the peer group was constructed as a composite peer group in which the cable subgroup is weighted 63% ( 63 % ) and the media subgroup is weighted 37% ( 37 % ) based on the respective revenue of our cable communications and nbcuniversal segments .
- `table-row-3` (table[3]): peer group index | 2011: $ 110 | 2012: $ 157 | 2013: $ 231 | 2014: $ 267 | 2015: $ 265

**Original gold annotations:**

```json
{
  "table_1": "the comcast class a of 2011 is $ 110 ; the comcast class a of 2012 is $ 177 ; the comcast class a of 2013 is $ 250 ; the comcast class a of 2014 is $ 282 ; the comcast class a of 2015 is $ 279 ;",
  "table_2": "the s&p 500 stock index of 2011 is $ 102 ; the s&p 500 stock index of 2012 is $ 118 ; the s&p 500 stock index of 2013 is $ 156 ; the s&p 500 stock index of 2014 is $ 177 ; the s&p 500 stock index of 2015 is $ 180 ;",
  "text_7": "the graph assumes $ 100 was invested on december 31 , 2010 in our class a common stock and in each of the following indices and assumes the reinvestment of dividends ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 066. [train] `IQV/2016/page_65.pdf-2`

**Question:** what is the percent increase in selling and administrative expenses from 2015 to 2016?

**Mapped positives:**

- `table-row-1` (table[1]): selling general and administrative expenses | year ended december 31 , 2016: $ 1011 | year ended december 31 , 2015: $ 815 | year ended december 31 , 2014: $ 781

**Five negative candidates:**

- `post-text-2` (post_text[2]): the constant currency increase in general corporate and unallocated expenses in 2016 was primarily due to higher stock-based compensation expense .
- `post-text-0` (post_text[0]): 2016 compared to 2015 the $ 196 million increase in selling , general and administrative expenses in 2016 included a constant currency increase of $ 215 million , or 26.4% ( 26.4 % ) , partially offset by a positive impact of approximately $ 19 million from the effects of foreign currency fluctuations .
- `post-text-3` (post_text[3]): 2015 compared to 2014 the $ 34 million increase in selling , general and administrative expenses in 2015 included a constant currency increase of $ 74 million , or 9.5% ( 9.5 % ) , partially offset by a positive impact of approximately $ 42 million from the effects of foreign currency fluctuations .
- `pre-text-2` (pre_text[2]): the constant currency growth was comprised of a $ 71 million increase in commercial solutions , which included the impact from the encore acquisition which closed in july 2014 , a $ 146 million increase in research & development solutions , which included the incremental impact from the businesses that quest contributed to q2 solutions , and a $ 21 million increase in integrated engagement services .
- `pre-text-3` (pre_text[3]): the decrease in costs of revenue as a percent of revenues for 2015 was primarily as a result of an improvement in constant currency profit margin in the commercial solutions , research & development solutions and integrated engagement services segments ( as more fully described in the segment discussion later in this section ) .

**Original gold annotations:**

```json
{
  "table_1": "( dollars in millions ) the selling general and administrative expenses of year ended december 31 , 2016 is $ 1011 ; the selling general and administrative expenses of year ended december 31 , 2015 is $ 815 ; the selling general and administrative expenses of year ended december 31 , 2014 is $ 781 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 067. [train] `CDW/2017/page_73.pdf-3`

**Question:** what was the greatest foreign currency translation loss , in millions?

**Mapped positives:**

- `table-row-1` (table[1]): foreign currency translation | years ended december 31 , 2017: $ -96.1 ( 96.1 ) | years ended december 31 , 2016: $ -139.6 ( 139.6 ) | years ended december 31 , 2015: $ -61.1 ( 61.1 )

**Five negative candidates:**

- `post-text-5` (post_text[5]): these items can be delivered to customers in a variety of ways , including ( i ) as physical product shipped from the company 2019s warehouse , ( ii ) via drop-shipment by the vendor or supplier , or ( iii ) via electronic delivery for software licenses .
- `table-row-2` (table[2]): unrealized gain from hedge accounting | years ended december 31 , 2017: 0.2 | years ended december 31 , 2016: 2014 | years ended december 31 , 2015: 2014
- `post-text-4` (post_text[4]): revenues from the sales of hardware products and software licenses are generally recognized on a gross basis with the selling price to the customer recorded as sales and the acquisition cost of the product recorded as cost of sales .
- `pre-text-1` (pre_text[1]): the company classifies deferred financing costs as a direct deduction from the carrying value of the long-term debt liability on the consolidated balance sheets , except for deferred financing costs associated with revolving credit facilities which are presented as an asset , within other assets on the consolidated balance sheets .
- `pre-text-10` (pre_text[10]): level 3 2013 inputs are generally unobservable and typically reflect management 2019s estimates of assumptions that market participants would use in pricing the asset or liability .

**Original gold annotations:**

```json
{
  "table_1": "( in millions ) the foreign currency translation of years ended december 31 , 2017 is $ -96.1 ( 96.1 ) ; the foreign currency translation of years ended december 31 , 2016 is $ -139.6 ( 139.6 ) ; the foreign currency translation of years ended december 31 , 2015 is $ -61.1 ( 61.1 ) ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 068. [dev] `AON/2009/page_48.pdf-2`

**Question:** what is the lowest segment operating income margin?

**Mapped positives:**

- `table-row-3` (table[3]): segment operating income margin | 2009: 16.0% ( 16.0 % ) | 2008: 15.3% ( 15.3 % ) | 2007: 13.4% ( 13.4 % )

**Five negative candidates:**

- `post-text-11` (post_text[11]): the prolonged economic downturn is adversely impacting our clients 2019 financial condition and the levels of business activities in the industries and geographies where we operate .
- `table-row-2` (table[2]): segment operating income | 2009: 203 | 2008: 208 | 2007: 180
- `post-text-8` (post_text[8]): strategic human capital delivers advice to complex global organizations on talent , change and organizational effectiveness issues , including talent strategy and acquisition , executive on-boarding , performance management , leadership assessment and development , communication strategy , workforce training and change management .
- `post-text-5` (post_text[5]): 3 .
- `post-text-9` (post_text[9]): outsourcing offers employment processing , performance improvement , benefits administration and other employment-related services .

**Original gold annotations:**

```json
{
  "table_3": "years ended december 31 , the segment operating income margin of 2009 is 16.0% ( 16.0 % ) ; the segment operating income margin of 2008 is 15.3% ( 15.3 % ) ; the segment operating income margin of 2007 is 13.4% ( 13.4 % ) ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 069. [train] `STT/2001/page_74.pdf-2`

**Question:** assuming that the outstanding number of shares is 100 million before the 2001 stock split , how many shares will be outstanding after the split , in millions?

**Mapped positives:**

- `post-text-1` (post_text[1]): in 1998 , the rights agreement was amended and restated , and in 2001 , the rights plan was impacted by the 2-for-1 stock split .

**Five negative candidates:**

- `table-row-1` (table[1]): unrealized gain on available-for-sale securities | 2001: $ 96 | 2000: $ 19
- `post-text-9` (post_text[9]): under capital adequacy guidelines , state street must meet specific capital guidelines that involve quantitative measures of state street 2019s assets , liabilities and off-balance sheet items as calculated under regulatory accounting practices .
- `table-row-2` (table[2]): foreign currency translation | 2001: -27 ( 27 ) | 2000: -20 ( 20 )
- `post-text-7` (post_text[7]): note k regulatory matters r e g u l a t o r y c a p i t a l state street is subject to various regulatory capital requirements administered by federal banking agencies .
- `pre-text-0` (pre_text[0]): a black-scholes option-pricing model was used for purposes of estimating the fair value of state street 2019s employee stock options at the grant date .

**Original gold annotations:**

```json
{
  "text_5": "in 1998 , the rights agreement was amended and restated , and in 2001 , the rights plan was impacted by the 2-for-1 stock split ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 070. [train] `GIS/2019/page_33.pdf-1`

**Question:** what was the change in the net earnings from 2018 to 2019 in million

**Mapped positives:**

- `pre-text-2` (pre_text[2]): a substantial portion of this operating cash flow has been returned to shareholders through share repurchases and dividends .
- `table-row-1` (table[1]): net earnings including earnings attributable to redeemable and noncontrollinginterests | fiscal year 2019: $ 1786.2 | fiscal year 2018: $ 2163.0

**Five negative candidates:**

- `table-row-5` (table[5]): stock-based compensation | fiscal year 2019: 84.9 | fiscal year 2018: 77.0
- `table-row-0` (table[0]): in millions | fiscal year 2019 | fiscal year 2018
- `post-text-5` (post_text[5]): corporate tax rate as a result of the tcja in fiscal we strive to grow core working capital at or below the rate of growth in our net sales .
- `pre-text-5` (pre_text[5]): as of may 26 , 2019 , we had $ 399 million of cash and cash equivalents held in foreign jurisdictions .
- `table-row-2` (table[2]): depreciation and amortization | fiscal year 2019: 620.1 | fiscal year 2018: 618.8

**Original gold annotations:**

```json
{
  "text_2": "a substantial portion of this operating cash flow has been returned to shareholders through share repurchases and dividends .",
  "table_1": "in millions the net earnings including earnings attributable to redeemable and noncontrollinginterests of fiscal year 2019 is $ 1786.2 ; the net earnings including earnings attributable to redeemable and noncontrollinginterests of fiscal year 2018 is $ 2163.0 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 071. [dev] `ABMD/2007/page_52.pdf-3`

**Question:** what portion of total future obligations is related to operating lease obligations as of march 31 , 2007?

**Mapped positives:**

- `table-row-1` (table[1]): operating lease obligations | payments due by fiscal year total: $ 7669 | payments due by fiscal year less than 1 year: $ 1960 | payments due by fiscal year 1-3 years: $ 3441 | payments due by fiscal year 3-5 years: $ 1652 | payments due by fiscal year more than 5 years: $ 616
- `table-row-3` (table[3]): total obligations | payments due by fiscal year total: $ 14090 | payments due by fiscal year less than 1 year: $ 8381 | payments due by fiscal year 1-3 years: $ 3441 | payments due by fiscal year 3-5 years: $ 1652 | payments due by fiscal year more than 5 years: $ 616

**Five negative candidates:**

- `post-text-3` (post_text[3]): we may make additional contingent payments to impella 2019s former shareholders based on additional milestone payments related to fda approvals in the amount of up to $ 11.2 million .
- `post-text-17` (post_text[17]): the maximum potential amount of future payments we could be required to make under these indemnification provisions is unlimited .
- `post-text-14` (post_text[14]): we enter into agreements with other companies in the ordinary course of business , typically with underwriters , contractors , clinical sites and customers that include indemnification provisions .
- `post-text-16` (post_text[16]): these indemnification provisions generally survive termination of the underlying agreement .
- `post-text-20` (post_text[20]): accordingly , we have no liabilities recorded for these agreements as of march 31 , 2007 .

**Original gold annotations:**

```json
{
  "table_1": "contractual obligations the operating lease obligations of payments due by fiscal year total is $ 7669 ; the operating lease obligations of payments due by fiscal year less than 1 year is $ 1960 ; the operating lease obligations of payments due by fiscal year 1-3 years is $ 3441 ; the operating lease obligations of payments due by fiscal year 3-5 years is $ 1652 ; the operating lease obligations of payments due by fiscal year more than 5 years is $ 616 ;",
  "table_3": "contractual obligations the total obligations of payments due by fiscal year total is $ 14090 ; the total obligations of payments due by fiscal year less than 1 year is $ 8381 ; the total obligations of payments due by fiscal year 1-3 years is $ 3441 ; the total obligations of payments due by fiscal year 3-5 years is $ 1652 ; the total obligations of payments due by fiscal year more than 5 years is $ 616 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 072. [train] `GPN/2008/page_88.pdf-2`

**Question:** what is the number of remaining shares under the repurchase authorization , assuming an average share price of $ 37.85?

**Mapped positives:**

- `post-text-10` (post_text[10]): under this authorization , we repurchased 2.3 million shares of our common stock during fiscal 2008 at a cost of $ 87.0 million , or an average of $ 37.85 per share , including commissions .
- `post-text-11` (post_text[11]): as of may 31 , 2008 , we had $ 13.0 million remaining under our current share repurchase authorization .

**Five negative candidates:**

- `post-text-8` (post_text[8]): we expect that the examination phase of the audit for the years 2004 to 2005 will conclude in fiscal 2009 .
- `post-text-0` (post_text[0]): as of may 31 , 2008 , the total amount of gross unrecognized tax benefits that , if recognized , would affect the effective tax rate is $ 3.7 million .
- `table-row-2` (table[2]): additions for tax positions of prior years | $ 3760: 50
- `table-row-1` (table[1]): additions based on tax positions related to the current year | $ 3760: 93
- `post-text-5` (post_text[5]): in the normal course of business , we are subject to examination by taxing authorities throughout the world , including such major jurisdictions as the united states and canada .

**Original gold annotations:**

```json
{
  "text_14": "under this authorization , we repurchased 2.3 million shares of our common stock during fiscal 2008 at a cost of $ 87.0 million , or an average of $ 37.85 per share , including commissions .",
  "text_15": "as of may 31 , 2008 , we had $ 13.0 million remaining under our current share repurchase authorization ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 073. [train] `AAL/2014/page_219.pdf-2`

**Question:** what was the unrecognized tax benefit at december 31 , 2013?

**Mapped positives:**

- `table-row-1` (table[1]): unrecognized tax benefit at january 1 | 2014: $ 5 | 2013: $ 5

**Five negative candidates:**

- `pre-text-0` (pre_text[0]): table of contents notes to consolidated financial statements of american airlines , inc .
- `pre-text-5` (pre_text[5]): american has an unrecognized tax benefit of approximately $ 5 million , which did not change during the twelve months ended december 31 , 2014 .
- `post-text-14` (post_text[14]): american 2019s current policy is not to enter into transactions to hedge its fuel consumption , although american reviews that policy from time to time based on market conditions and other factors. .
- `post-text-1` (post_text[1]): 8 .
- `table-row-2` (table[2]): no activity | 2014: 2014 | 2013: 2014

**Original gold annotations:**

```json
{
  "table_1": "the unrecognized tax benefit at january 1 of 2014 is $ 5 ; the unrecognized tax benefit at january 1 of 2013 is $ 5 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 074. [train] `CB/2008/page_218.pdf-2`

**Question:** what is the net change in the number of unvested restricted stocks in 2008?

**Mapped positives:**

- `table-row-9` (table[9]): unvested restricted stock december 31 2007 | number of restricted stock: 3821707 | weighted average grant- date fair value: $ 53.12
- `table-row-13` (table[13]): unvested restricted stock december 31 2008 | number of restricted stock: 3883230 | weighted average grant- date fair value: $ 57.01

**Five negative candidates:**

- `post-text-1` (post_text[1]): therefore , upon adoption of fas 123r , the amount of deferred compensation that had been reflected in unearned stock grant compensation was reclassified to additional paid-in capital in the company 2019s consolidated balance sheet .
- `post-text-9` (post_text[9]): delivery of common shares on account of these restricted stock units to non-management directors is deferred until six months after the date of the non-management directors 2019 termination from the board .
- `pre-text-0` (pre_text[0]): n o t e s t o c o n s o l i d a t e d f i n a n c i a l s t a t e m e n t s ( continued ) ace limited and subsidiaries the following table shows changes in the company 2019s restricted stock for the years ended december 31 , 2008 , 2007 , and 2006 : number of restricted stock weighted average grant- date fair value .
- `table-row-0` (table[0]): | number of restricted stock | weighted average grant- date fair value
- `post-text-16` (post_text[16]): prior to the second subscription period of 2007 , the purchase price was calculated as the lower of ( i ) 85 percent of the fair value of a common share on the first day of the subscription period , or .

**Original gold annotations:**

```json
{
  "table_9": "the unvested restricted stock december 31 2007 of number of restricted stock is 3821707 ; the unvested restricted stock december 31 2007 of weighted average grant- date fair value is $ 53.12 ;",
  "table_13": "the unvested restricted stock december 31 2008 of number of restricted stock is 3883230 ; the unvested restricted stock december 31 2008 of weighted average grant- date fair value is $ 57.01 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 075. [train] `UNP/2008/page_59.pdf-3`

**Question:** what percentage of total freight revenues were energy in 2008?

**Mapped positives:**

- `table-row-4` (table[4]): energy | 2008: 3810 | 2007: 3134 | 2006: 2949
- `table-row-7` (table[7]): total freight revenues | 2008: $ 17118 | 2007: $ 15486 | 2006: $ 14791

**Five negative candidates:**

- `post-text-0` (post_text[0]): basis of presentation 2013 certain prior year amounts have been reclassified to conform to the current period financial statement presentation .
- `post-text-3` (post_text[3]): in addition , we modified our operating expense categories to report fuel used in railroad operations as a stand-alone category , to combine purchased services and materials into one line , and to reclassify certain other expenses among operating expense categories .
- `post-text-8` (post_text[8]): the corporation evaluates its less than majority-owned investments for consolidation .
- `pre-text-0` (pre_text[0]): notes to the consolidated financial statements union pacific corporation and subsidiary companies for purposes of this report , unless the context otherwise requires , all references herein to the 201ccorporation 201d , 201cupc 201d , 201cwe 201d , 201cus 201d , and 201cour 201d mean union pacific corporation and its subsidiaries , including union pacific railroad company , which will be separately referred to herein as 201cuprr 201d or the 201crailroad 201d .
- `pre-text-6` (pre_text[6]): the railroad , along with its subsidiaries and rail affiliates , is our one reportable operating segment .

**Original gold annotations:**

```json
{
  "table_4": "millions of dollars the energy of 2008 is 3810 ; the energy of 2007 is 3134 ; the energy of 2006 is 2949 ;",
  "table_7": "millions of dollars the total freight revenues of 2008 is $ 17118 ; the total freight revenues of 2007 is $ 15486 ; the total freight revenues of 2006 is $ 14791 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 076. [train] `ETR/2011/page_22.pdf-1`

**Question:** what is the net change in amount of net revenue from 2009 to 2010?

**Mapped positives:**

- `table-row-1` (table[1]): 2009 net revenue | amount ( in millions ): $ 4694
- `table-row-9` (table[9]): 2010 net revenue | amount ( in millions ): $ 5051

**Five negative candidates:**

- `pre-text-4` (pre_text[4]): these costs are discussed in more detail below and throughout this section .
- `table-row-4` (table[4]): provision for regulatory proceedings | amount ( in millions ): 26
- `table-row-3` (table[3]): retail electric price | amount ( in millions ): 137
- `pre-text-2` (pre_text[2]): in april 2010 , entergy announced that it planned to unwind the business infrastructure associated with the proposed spin-off transaction .
- `pre-text-1` (pre_text[1]): in november 2007 the board approved a plan to pursue a separation of entergy 2019s non-utility nuclear business from entergy through a spin-off of the business to entergy shareholders .

**Original gold annotations:**

```json
{
  "table_1": "the 2009 net revenue of amount ( in millions ) is $ 4694 ;",
  "table_9": "the 2010 net revenue of amount ( in millions ) is $ 5051 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 077. [train] `PNC/2014/page_232.pdf-2`

**Question:** what was the average balance in millions for commercial mortgage recourse obligations as of december 31 2014 and 2013?

**Mapped positives:**

- `table-row-4` (table[4]): december 31 | 2014: $ 35 | 2013: $ 33

**Five negative candidates:**

- `post-text-1` (post_text[1]): these loan repurchase obligations primarily relate to situations where pnc is alleged to have breached certain origination covenants and representations and warranties made to purchasers of the loans in the respective purchase and sale agreements .
- `table-row-1` (table[1]): january 1 | 2014: $ 33 | 2013: $ 43
- `pre-text-25` (pre_text[25]): table 150 : analysis of commercial mortgage recourse obligations .
- `pre-text-23` (pre_text[23]): if payment is required under these programs , we would not have a contractual interest in the collateral underlying the mortgage loans on which losses occurred , although the value of the collateral is taken into account in determining our share of such losses .
- `pre-text-14` (pre_text[14]): recourse and repurchase obligations as discussed in note 2 loan sale and servicing activities and variable interest entities , pnc has sold commercial mortgage , residential mortgage and home equity loans/ lines of credit directly or indirectly through securitization and loan sale transactions in which we have continuing involvement .

**Original gold annotations:**

```json
{
  "table_4": "in millions the december 31 of 2014 is $ 35 ; the december 31 of 2013 is $ 33 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 078. [train] `C/2010/page_226.pdf-1`

**Question:** what is the ratio of the goodwill for north america regional consumer banking to emea regional consumer banking

**Mapped positives:**

- `table-row-1` (table[1]): north america regional consumer banking | fair value as a % (  % ) of allocated book value: 170% ( 170 % ) | goodwill: $ 2518
- `table-row-2` (table[2]): emea regional consumer banking | fair value as a % (  % ) of allocated book value: 168 | goodwill: 338

**Five negative candidates:**

- `post-text-16` (post_text[16]): if the future were to differ adversely from management 2019s best estimate of key economic assumptions , and associated cash flows were to decrease by a small margin , citi could potentially experience future material impairment charges with respect to $ 4560 million of goodwill remaining in the local consumer lending 2014 cards reporting unit .
- `post-text-4` (post_text[4]): the selection of the multiple considers the operating performance and financial condition of the local consumer lending 2014cards operations as compared with those of a group of selected publicly traded guideline companies and a group of selected acquired companies .
- `post-text-6` (post_text[6]): since the guideline company prices used are on a minority interest basis , the selection of the multiple considers the guideline acquisition prices , which reflect control rights and privileges , in arriving at a multiple that reflects an appropriate control premium .
- `pre-text-1` (pre_text[1]): in millions of dollars reporting unit ( 1 ) fair value as a % (  % ) of allocated book value goodwill .
- `table-row-4` (table[4]): latin america regional consumer banking | fair value as a % (  % ) of allocated book value: 230 | goodwill: 1800

**Original gold annotations:**

```json
{
  "table_1": "reporting unit ( 1 ) the north america regional consumer banking of fair value as a % ( % ) of allocated book value is 170% ( 170 % ) ; the north america regional consumer banking of goodwill is $ 2518 ;",
  "table_2": "reporting unit ( 1 ) the emea regional consumer banking of fair value as a % ( % ) of allocated book value is 168 ; the emea regional consumer banking of goodwill is 338 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 079. [train] `C/2008/page_159.pdf-3`

**Question:** what was the percentage of the company 2019s net deferred tax asset attributable to the net u.s . federal dtas

**Mapped positives:**

- `post-text-27` (post_text[27]): the company 2019s net deferred tax asset ( dta ) of $ 44.5 billion consists of approximately $ 36.5 billion of net u.s .
- `post-text-28` (post_text[28]): federal dtas , $ 4 billion of net state dtas and $ 4 billion of net foreign dtas .

**Five negative candidates:**

- `post-text-13` (post_text[13]): foreign tax credits ) of $ 6.1 billion would have to be provided if such earnings were remitted currently .
- `post-text-12` (post_text[12]): federal income tax rate , additional taxes ( net of u.s .
- `post-text-15` (post_text[15]): income taxes are not provided for on the company 2019s savings bank base year bad debt reserves that arose before 1988 because under current u.s .
- `table-row-1` (table[1]): united states | tax year: 2003
- `pre-text-3` (pre_text[3]): one of the issues relates to the timing of the inclusion of interchange fees received by the company relating to credit card purchases by its cardholders .

**Original gold annotations:**

```json
{
  "text_41": "the company 2019s net deferred tax asset ( dta ) of $ 44.5 billion consists of approximately $ 36.5 billion of net u.s .",
  "text_42": "federal dtas , $ 4 billion of net state dtas and $ 4 billion of net foreign dtas ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 080. [dev] `GPN/2009/page_70.pdf-2`

**Question:** what portion of total assets acquired is composed of goodwill?

**Mapped positives:**

- `table-row-1` (table[1]): goodwill | total: $ 13536
- `table-row-6` (table[6]): total assets acquired | total: 19427

**Five negative candidates:**

- `post-text-8` (post_text[8]): the .
- `pre-text-0` (pre_text[0]): notes to consolidated financial statements 2014 ( continued ) in connection with these discover related purchases , we have sold the contractual rights to future commissions on discover transactions to certain of our isos .
- `table-row-7` (table[7]): current liabilities | total: -2347 ( 2347 )
- `table-row-2` (table[2]): customer-related intangible assets | total: 4091
- `table-row-5` (table[5]): other current assets | total: 502

**Original gold annotations:**

```json
{
  "table_1": "the goodwill of total is $ 13536 ;",
  "table_6": "the total assets acquired of total is 19427 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 081. [train] `AMT/2016/page_69.pdf-3`

**Question:** what portion of the total capital expenditures is related to redevelopment?

**Mapped positives:**

- `table-row-3` (table[3]): redevelopment | $ 149.7: 147.4
- `table-row-5` (table[5]): total capital expenditures | $ 149.7: $ 701.4

**Five negative candidates:**

- `pre-text-4` (pre_text[4]): while certain subsidiaries may pay us interest or principal on intercompany debt , it has not been our practice to repatriate earnings from our foreign subsidiaries primarily due to our ongoing expansion efforts and related capital needs .
- `pre-text-6` (pre_text[6]): cash flows from operating activities for the year ended december 31 , 2016 , cash provided by operating activities increased $ 520.6 million as compared to the year ended december 31 , 2015 .
- `pre-text-9` (pre_text[9]): the primary factors that impacted cash provided by operating activities as compared to the year ended december 31 , 2014 , include : 2022 an increase in our operating profit of $ 433.3 million ; 2022 an increase of approximately $ 87.8 million in cash paid for taxes , driven primarily by the mipt one-time cash tax charge of $ 93.0 million ; 2022 a decrease in capital contributions , tenant settlements and other prepayments of approximately $ 99.0 million ; 2022 an increase of approximately $ 29.9 million in cash paid for interest ; 2022 a decrease of approximately $ 34.9 million in termination and decommissioning fees ; 2022 a decrease of approximately $ 49.0 million in tenant receipts due to timing ; and 2022 a decrease due to the non-recurrence of a 2014 value added tax refund of approximately $ 60.3 million .
- `table-row-2` (table[2]): capital improvements and corporate expenditures ( 2 ) | $ 149.7: 126.7
- `pre-text-1` (pre_text[1]): during the year ended december 31 , 2016 , we generated sufficient cash flow from operations to fund our capital expenditures and debt service obligations , as well as our required distributions .

**Original gold annotations:**

```json
{
  "table_3": "discretionary capital projects ( 1 ) the redevelopment of $ 149.7 is 147.4 ;",
  "table_5": "discretionary capital projects ( 1 ) the total capital expenditures of $ 149.7 is $ 701.4 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 082. [train] `RL/2010/page_11.pdf-2`

**Question:** what percentage of doors in the wholesale segment as of april 3 , 2010 where in the united states and canada geography?

**Mapped positives:**

- `table-row-1` (table[1]): united states and canada | number of doors ( a ): 4402
- `table-row-4` (table[4]): total | number of doors ( a ): 8940

**Five negative candidates:**

- `post-text-11` (post_text[11]): as of april 3 , 2010 , we had approximately 14000 shop-within-shops dedicated to our ralph lauren-branded wholesale products worldwide .
- `post-text-18` (post_text[18]): the extension of our direct-to-consumer reach is a primary long-term strategic goal .
- `post-text-13` (post_text[13]): we normally share in the cost of these shop-within-shops with our wholesale customers .
- `post-text-15` (post_text[15]): basic products such as knit shirts , chino pants and oxford cloth shirts can be ordered at any time through our basic stock replenishment programs .
- `post-text-7` (post_text[7]): in addition , we maintain regional showrooms in atlanta , chicago , dallas , milan , paris , london , munich , madrid and stockholm .

**Original gold annotations:**

```json
{
  "table_1": "location the united states and canada of number of doors ( a ) is 4402 ;",
  "table_4": "location the total of number of doors ( a ) is 8940 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 083. [dev] `JKHY/2014/page_30.pdf-1`

**Question:** what was the cumulative total return on the s & p 500 for the five year period?

**Mapped positives:**

- `table-row-4` (table[4]): s & p 500 | 2009: 100.00 | 2010: 114.43 | 2011: 149.55 | 2012: 157.70 | 2013: 190.18 | 2014: 236.98

**Five negative candidates:**

- `table-row-1` (table[1]): jkhy | 2009: 100.00 | 2010: 116.85 | 2011: 148.92 | 2012: 173.67 | 2013: 240.25 | 2014: 307.57
- `table-row-0` (table[0]): | 2009 | 2010 | 2011 | 2012 | 2013 | 2014
- `post-text-2` (post_text[2]): peer companies selected are in the business of providing specialized computer software , hardware and related services to financial institutions and other businesses .
- `post-text-3` (post_text[3]): in fiscal 2014 , we changed our peer group of companies used for this analysis to maintain alignment with peer companies selected by our compensation committee for use in determining compensation for executive management .
- `table-row-3` (table[3]): new peer group | 2009: 100.00 | 2010: 115.50 | 2011: 159.31 | 2012: 171.86 | 2013: 198.72 | 2014: 273.95

**Original gold annotations:**

```json
{
  "table_4": "the s & p 500 of 2009 is 100.00 ; the s & p 500 of 2010 is 114.43 ; the s & p 500 of 2011 is 149.55 ; the s & p 500 of 2012 is 157.70 ; the s & p 500 of 2013 is 190.18 ; the s & p 500 of 2014 is 236.98 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 084. [train] `CB/2009/page_233.pdf-1`

**Question:** what percent of the direct amount is ceded to other companies in 2009 , ( in millions ) ?

**Mapped positives:**

- `table-row-1` (table[1]): 2009 | direct amount: $ 15415 | ceded to other companies: $ 5943 | assumed from other companies: $ 3768 | net amount: $ 13240 | percentage of amount assumed to net: 28% ( 28 % )

**Five negative candidates:**

- `pre-text-1` (pre_text[1]): dollars , except for percentages ) direct amount ceded to companies assumed from other companies net amount percentage of amount assumed to .
- `table-row-3` (table[3]): 2007 | direct amount: $ 14673 | ceded to other companies: $ 5834 | assumed from other companies: $ 3458 | net amount: $ 12297 | percentage of amount assumed to net: 28% ( 28 % )
- `table-row-2` (table[2]): 2008 | direct amount: $ 16087 | ceded to other companies: $ 6144 | assumed from other companies: $ 3260 | net amount: $ 13203 | percentage of amount assumed to net: 25% ( 25 % )
- `post-text-0` (post_text[0]): .
- `table-row-0` (table[0]): for the years ended december 31 2009 2008 and 2007 ( in millions of u.s . dollars except for percentages ) | direct amount | ceded to other companies | assumed from other companies | net amount | percentage of amount assumed to net

**Original gold annotations:**

```json
{
  "table_1": "for the years ended december 31 2009 2008 and 2007 ( in millions of u.s . dollars except for percentages ) the 2009 of direct amount is $ 15415 ; the 2009 of ceded to other companies is $ 5943 ; the 2009 of assumed from other companies is $ 3768 ; the 2009 of net amount is $ 13240 ; the 2009 of percentage of amount assumed to net is 28% ( 28 % ) ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 085. [dev] `UNP/2008/page_79.pdf-3`

**Question:** what was the percentage difference in sold receivables from 2007 to 2008?

**Mapped positives:**

- `post-text-19` (post_text[19]): the railroad collected approximately $ 17.8 billion and $ 16.1 billion during the years ended december 31 , 2008 and 2007 , respectively .

**Five negative candidates:**

- `post-text-6` (post_text[6]): upri sells , without recourse on a 364-day revolving basis , an undivided interest in such accounts receivable to investors .
- `post-text-13` (post_text[13]): this retained interest is included in accounts receivable in our consolidated financial statements .
- `pre-text-2` (pre_text[2]): as of december 31 , 2008 and 2007 , we had no interest rate cash flow hedges outstanding .
- `post-text-0` (post_text[0]): fair value of debt instruments 2013 the fair value of our short- and long-term debt was estimated using quoted market prices , where available , or current borrowing rates .
- `post-text-3` (post_text[3]): at december 31 , 2008 and 2007 , approximately $ 320 million and $ 181 million , respectively , of fixed-rate debt securities contained call provisions that allowed us to retire the debt instruments prior to final maturity , with the payment of fixed call premiums , or in certain cases , at par .

**Original gold annotations:**

```json
{
  "text_23": "the railroad collected approximately $ 17.8 billion and $ 16.1 billion during the years ended december 31 , 2008 and 2007 , respectively ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 086. [train] `HFC/2011/page_92.pdf-5`

**Question:** what percentage of the fair value of performance share units at july 1 , 2011 was relates to to post-merger services and will be recognized ratably over the remaining service period through 2013?

**Mapped positives:**

- `pre-text-3` (pre_text[3]): the number of shares ultimately issued for each award will be based on our financial performance as compared to peer group companies over the performance period and can range from zero to 200% ( 200 % ) .
- `pre-text-4` (pre_text[4]): as of december 31 , 2011 , estimated share payouts for outstanding non-vested performance share unit awards ranged from 150% ( 150 % ) to 195% ( 195 % ) .
- `pre-text-9` (pre_text[9]): of this amount , $ 7.3 million relates to post-merger services and will be recognized ratably over the remaining service period through 2013 .
- `pre-text-8` (pre_text[8]): the fair value of these performance share units at july 1 , 2011 was $ 8.6 million .

**Five negative candidates:**

- `pre-text-7` (pre_text[7]): these performance share units were valued at july 1 , 2011 using a monte carlo valuation model , which simulates future stock price movements using key inputs including grant date and measurement date stock prices , expected stock price performance , expected rate of return and volatility of our stock price relative to the peer group over the three-year performance period .
- `post-text-9` (post_text[9]): interest income is recorded as earned .
- `pre-text-5` (pre_text[5]): for the legacy frontier performance share units assumed at july 1 , 2011 , performance is based on market performance criteria , which is calculated as the total shareholder return achieved by hollyfrontier stockholders compared with the average shareholder return achieved by an equally-weighted peer group of independent refining companies over a three-year period .
- `table-row-1` (table[1]): outstanding at january 1 2011 ( non-vested ) | grants: 556186
- `post-text-2` (post_text[2]): based on the weighted average grant date fair value of $ 20.71 there was $ 11.7 million of total unrecognized compensation cost related to non-vested performance share units .

**Original gold annotations:**

```json
{
  "text_3": "the number of shares ultimately issued for each award will be based on our financial performance as compared to peer group companies over the performance period and can range from zero to 200% ( 200 % ) .",
  "text_4": "as of december 31 , 2011 , estimated share payouts for outstanding non-vested performance share unit awards ranged from 150% ( 150 % ) to 195% ( 195 % ) .",
  "text_9": "of this amount , $ 7.3 million relates to post-merger services and will be recognized ratably over the remaining service period through 2013 .",
  "text_8": "the fair value of these performance share units at july 1 , 2011 was $ 8.6 million ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 087. [train] `GS/2013/page_52.pdf-3`

**Question:** what percentage of total net revenues institutional client services segment in 2012 were made up of equities client execution?

**Mapped positives:**

- `table-row-2` (table[2]): equities client execution1 | year ended december 2013: 2594 | year ended december 2012: 3171 | year ended december 2011: 3031
- `table-row-6` (table[6]): total net revenues | year ended december 2013: 15721 | year ended december 2012: 18124 | year ended december 2011: 17280

**Five negative candidates:**

- `table-row-8` (table[8]): pre-tax earnings | year ended december 2013: $ 3939 | year ended december 2012: $ 5644 | year ended december 2011: $ 4443
- `pre-text-0` (pre_text[0]): management 2019s discussion and analysis institutional client services our institutional client services segment is comprised of : fixed income , currency and commodities client execution .
- `post-text-3` (post_text[3]): see note 12 to the consolidated financial statements for further information about this sale .
- `pre-text-6` (pre_text[6]): given the focus on the mortgage market , our mortgage activities are further described below .
- `pre-text-8` (pre_text[8]): government agency-issued collateralized mortgage obligations , other prime , subprime and alt-a securities and loans ) , and other asset-backed securities , loans and derivatives .

**Original gold annotations:**

```json
{
  "table_2": "in millions the equities client execution1 of year ended december 2013 is 2594 ; the equities client execution1 of year ended december 2012 is 3171 ; the equities client execution1 of year ended december 2011 is 3031 ;",
  "table_6": "in millions the total net revenues of year ended december 2013 is 15721 ; the total net revenues of year ended december 2012 is 18124 ; the total net revenues of year ended december 2011 is 17280 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 088. [train] `FITB/2008/page_69.pdf-3`

**Question:** what is the percentage change in the balance of noncancelable lease obligations from 2007 to 2008?

**Mapped positives:**

- `table-row-4` (table[4]): noncancelable lease obligations | 2008: 937 | 2007: 734

**Five negative candidates:**

- `pre-text-24` (pre_text[24]): the obligations were issued to first charter capital trust i and ii , respectively .
- `pre-text-16` (pre_text[16]): the bancorp entered into interest rate swaps to convert the fixed-rate debt into floating rate .
- `table-row-6` (table[6]): capital expenditures | 2008: 68 | 2007: 94
- `post-text-9` (post_text[9]): at december 31 , 2008 , the reserve related to these standby letters of credit was $ 3 million .
- `pre-text-29` (pre_text[29]): at december 31 , 2008 , $ 2.5 billion of fhlb advances are floating rate .

**Original gold annotations:**

```json
{
  "table_4": "( $ in millions ) the noncancelable lease obligations of 2008 is 937 ; the noncancelable lease obligations of 2007 is 734 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 089. [train] `AWK/2018/page_172.pdf-4`

**Question:** what percentage of future annual commitments related to minimum quantities of purchased water having non-cancelable are due after 2023?

**Mapped positives:**

- `table-row-1` (table[1]): 2019 | amount: $ 65
- `table-row-2` (table[2]): 2020 | amount: 65
- `table-row-3` (table[3]): 2021 | amount: 65
- `table-row-4` (table[4]): 2022 | amount: 64
- `table-row-5` (table[5]): 2023 | amount: 57
- `table-row-6` (table[6]): thereafter | amount: 641

**Five negative candidates:**

- `post-text-4` (post_text[4]): for certain matters , claims and actions , the company is unable to estimate possible losses .
- `pre-text-4` (pre_text[4]): the company 2019s regulated subsidiaries maintain agreements with other water purveyors for the purchase of water to supplement their water supply .
- `post-text-2` (post_text[2]): contingencies the company is routinely involved in legal actions incident to the normal conduct of its business .
- `pre-text-5` (pre_text[5]): the following table provides the future annual commitments related to minimum quantities of purchased water having non-cancelable: .
- `post-text-8` (post_text[8]): chemical spill in west virginia .

**Original gold annotations:**

```json
{
  "table_1": "the 2019 of amount is $ 65 ;",
  "table_2": "the 2020 of amount is 65 ;",
  "table_3": "the 2021 of amount is 65 ;",
  "table_4": "the 2022 of amount is 64 ;",
  "table_5": "the 2023 of amount is 57 ;",
  "table_6": "the thereafter of amount is 641 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 090. [train] `JPM/2015/page_92.pdf-1`

**Question:** in 2015 what was the percent of the markets-based net interest income to the net interest income 2013 managed basis

**Mapped positives:**

- `table-row-1` (table[1]): net interest income 2013 managed basis ( a ) ( b ) | 2015: $ 44620 | 2014: $ 44619 | 2013: $ 44016
- `table-row-2` (table[2]): less : markets-based net interest income | 2015: 4813 | 2014: 5552 | 2013: 5492

**Five negative candidates:**

- `pre-text-7` (pre_text[7]): 2015 compared with 2014 net interest income excluding cib 2019s markets-based activities increased by $ 740 million in 2015 to $ 39.8 billion , and average interest-earning assets increased by $ 56.2 billion to $ 1.6 trillion .
- `post-text-0` (post_text[0]): management 2019s discussion and analysis 82 jpmorgan chase & co./2015 annual report net interest income excluding markets-based activities ( formerly core net interest income ) in addition to reviewing net interest income on a managed basis , management also reviews net interest income excluding cib 2019s markets-based activities to assess the performance of the firm 2019s lending , investing ( including asset-liability management ) and deposit-raising activities .
- `pre-text-11` (pre_text[11]): these changes in net interest income and interest-earning assets resulted in the net interest yield decreasing by 4 basis points to 2.50% ( 2.50 % ) for 2014 compared with 2013 net interest income excluding cib 2019s markets-based activities increased by $ 543 million in 2014 to $ 39.1 billion , and average interest-earning assets increased by $ 72.8 billion to $ 1.5 trillion .
- `table-row-7` (table[7]): net interest yield on average interest-earning assets 2013 managed basis | 2015: 2.14% ( 2.14 % ) | 2014: 2.18% ( 2.18 % ) | 2013: 2.23% ( 2.23 % )
- `pre-text-2` (pre_text[2]): management believes this exclusion provides investors and analysts with another measure by which to analyze the non-markets-related business trends of the firm and provides a comparable measure to other financial institutions that are primarily focused on lending , investing and deposit-raising activities .

**Original gold annotations:**

```json
{
  "table_1": "year ended december 31 ( in millions except rates ) the net interest income 2013 managed basis ( a ) ( b ) of 2015 is $ 44620 ; the net interest income 2013 managed basis ( a ) ( b ) of 2014 is $ 44619 ; the net interest income 2013 managed basis ( a ) ( b ) of 2013 is $ 44016 ;",
  "table_2": "year ended december 31 ( in millions except rates ) the less : markets-based net interest income of 2015 is 4813 ; the less : markets-based net interest income of 2014 is 5552 ; the less : markets-based net interest income of 2013 is 5492 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 091. [dev] `FIS/2007/page_94.pdf-3`

**Question:** what is the percentage change in rent expense from 2006 yo 2007?

**Mapped positives:**

- `post-text-1` (post_text[1]): rent expense incurred under all operating leases during the years ended december 31 , 2007 , 2006 and 2005 was $ 106.4 million , $ 81.5 million and $ 61.1 million , respectively .

**Five negative candidates:**

- `post-text-9` (post_text[9]): plan .
- `table-row-6` (table[6]): total | 83382: $ 249038
- `pre-text-5` (pre_text[5]): future minimum operating lease payments for leases with remaining terms greater than one year for each of the years in the five years ending december 31 , 2012 , and thereafter in the aggregate , are as follows ( in thousands ) : .
- `table-row-1` (table[1]): 2009 | 83382: 63060
- `table-row-5` (table[5]): thereafter | 83382: 30869

**Original gold annotations:**

```json
{
  "text_7": "rent expense incurred under all operating leases during the years ended december 31 , 2007 , 2006 and 2005 was $ 106.4 million , $ 81.5 million and $ 61.1 million , respectively ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 092. [train] `ETR/2017/page_25.pdf-1`

**Question:** what is the percent change in net revenue from 2015 to 2016?

**Mapped positives:**

- `table-row-1` (table[1]): 2015 net revenue | amount ( in millions ): $ 5829
- `table-row-7` (table[7]): 2016 net revenue | amount ( in millions ): $ 6179
- `pre-text-5` (pre_text[5]): net revenue utility following is an analysis of the change in net revenue comparing 2016 to 2015 .
- `pre-text-6` (pre_text[6]): amount ( in millions ) .

**Five negative candidates:**

- `table-row-0` (table[0]): | amount ( in millions )
- `post-text-5` (post_text[5]): see note 14 to the financial statements for discussion of the union power station purchase .
- `pre-text-2` (pre_text[2]): results of operations for 2015 also include the sale in december 2015 of the 583 mw rhode island state energy center for a realized gain of $ 154 million ( $ 100 million net-of-tax ) on the sale and the $ 77 million ( $ 47 million net-of-tax ) write-off and regulatory charges to recognize that a portion of the assets associated with the waterford 3 replacement steam generator project is no longer probable of recovery .
- `pre-text-0` (pre_text[0]): ( $ 66 million net-of-tax ) as a result of customer credits to be realized by electric customers of entergy louisiana , consistent with the terms of the stipulated settlement in the business combination proceeding .
- `table-row-6` (table[6]): other | amount ( in millions ): -43 ( 43 )

**Original gold annotations:**

```json
{
  "table_1": "the 2015 net revenue of amount ( in millions ) is $ 5829 ;",
  "table_7": "the 2016 net revenue of amount ( in millions ) is $ 6179 ;",
  "text_5": "net revenue utility following is an analysis of the change in net revenue comparing 2016 to 2015 .",
  "text_6": "amount ( in millions ) ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 093. [train] `JPM/2009/page_183.pdf-5`

**Question:** what was the net fair value of derivatives , in millions?

**Mapped positives:**

- `table-row-1` (table[1]): gross derivative fair value | derivative receivables: $ 1565518 | derivative payables: $ 1519183

**Five negative candidates:**

- `table-row-2` (table[2]): nettingadjustment 2013 offsetting receivables/payables | derivative receivables: -1419840 ( 1419840 ) | derivative payables: -1419840 ( 1419840 )
- `post-text-27` (post_text[27]): credit-linked notes a credit linked note ( 201ccln 201d ) is a funded credit derivative where the issuer of the cln purchases credit protection on a referenced entity from the note investor .
- `post-text-6` (post_text[6]): credit derivatives expose the protection purchaser to the creditworthiness of the protection seller , as the protection seller is required to make payments under the contract when the reference entity experiences a credit event , such as a bankruptcy , a failure to pay its obligation or a restructuring .
- `post-text-14` (post_text[14]): following is a summary of various types of credit derivatives .
- `post-text-13` (post_text[13]): in accomplishing the above , the firm uses different types of credit derivatives .

**Original gold annotations:**

```json
{
  "table_1": "december 31 2009 ( in millions ) the gross derivative fair value of derivative receivables is $ 1565518 ; the gross derivative fair value of derivative payables is $ 1519183 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 094. [train] `UAA/2018/page_40.pdf-4`

**Question:** what is the gross margin in 2018?

**Mapped positives:**

- `table-row-7` (table[7]): total net revenues | year ended december 31 , 2018: $ 5193185 | year ended december 31 , 2017: $ 4989244 | year ended december 31 , $ change: $ 203941 | year ended december 31 , % (  % ) change: 4.1% ( 4.1 % )
- `post-text-4` (post_text[4]): gross profit increased $ 89.1 million to $ 2340.5 million in 2018 from $ 2251.4 million in 2017 .

**Five negative candidates:**

- `post-text-5` (post_text[5]): gross profit as a percentage of net revenues , or gross margin , was unchanged at 45.1% ( 45.1 % ) in 2018 compared to 2017 .
- `post-text-2` (post_text[2]): license revenues increased $ 8.2 million , or 7.0% ( 7.0 % ) , to $ 124.8 million in 2018 from $ 116.6 million in 2017 .
- `post-text-12` (post_text[12]): this decrease was partially offset by higher costs in connection with brand marketing campaigns and increased marketing investments with the growth of our international business .
- `post-text-15` (post_text[15]): this increase was primarily due to higher incentive compensation expense and higher costs incurred for the continued expansion of our direct to consumer distribution channel and international business .
- `post-text-7` (post_text[7]): with the exception of improvements in product input costs and air freight improvements , we do not expect these trends to have a material impact on the full year 2019 .

**Original gold annotations:**

```json
{
  "table_7": "( in thousands ) the total net revenues of year ended december 31 , 2018 is $ 5193185 ; the total net revenues of year ended december 31 , 2017 is $ 4989244 ; the total net revenues of year ended december 31 , $ change is $ 203941 ; the total net revenues of year ended december 31 , % ( % ) change is 4.1% ( 4.1 % ) ;",
  "text_6": "gross profit increased $ 89.1 million to $ 2340.5 million in 2018 from $ 2251.4 million in 2017 ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 095. [train] `GPN/2008/page_99.pdf-3`

**Question:** what is the total amount of principle payment paid from 2008 to 2011?

**Mapped positives:**

- `pre-text-6` (pre_text[6]): the term loan calls for quarterly principal payments of $ 5 million beginning with the quarter ending august 31 , 2008 and increasing to $ 10 million beginning with the quarter ending august 31 , 2010 and $ 15 million beginning with the quarter ending august 31 , 2011 .

**Five negative candidates:**

- `pre-text-2` (pre_text[2]): on june 23 , 2008 , we entered into a new five year , $ 200 million term loan to fund a portion of the acquisition .
- `pre-text-5` (pre_text[5]): as of july 1 , 2008 , the interest rate on the term loan was 3.605% ( 3.605 % ) .
- `table-row-4` (table[4]): trademark | total: 2204
- `post-text-3` (post_text[3]): the contract-based intangible assets have amortization periods of 7 years .
- `pre-text-17` (pre_text[17]): the following table summarizes the preliminary purchase price allocation: .

**Original gold annotations:**

```json
{
  "text_6": "the term loan calls for quarterly principal payments of $ 5 million beginning with the quarter ending august 31 , 2008 and increasing to $ 10 million beginning with the quarter ending august 31 , 2010 and $ 15 million beginning with the quarter ending august 31 , 2011 ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 096. [train] `SNA/2012/page_82.pdf-1`

**Question:** what was the percent of income taxes as part of the the total other accrued liabilities in 2012

**Mapped positives:**

- `table-row-8` (table[8]): total other accrued liabilities | 2012: $ 247.9 | 2011: $ 255.9
- `table-row-1` (table[1]): income taxes | 2012: $ 19.6 | 2011: $ 11.7

**Five negative candidates:**

- `pre-text-3` (pre_text[3]): additions to the allowances for doubtful accounts are maintained through adjustments to the provision for credit losses , which are charged to current period earnings ; amounts determined to be uncollectable are charged directly against the allowances , while amounts recovered on previously charged-off accounts increase the allowances .
- `post-text-2` (post_text[2]): allowances for raw materials are largely based on an analysis of raw material age and actual physical inspection of raw material for fitness for use .
- `pre-text-4` (pre_text[4]): net charge-offs include the principal amount of losses charged off as well as charged-off interest and fees .
- `pre-text-2` (pre_text[2]): in circumstances where the company is aware of a specific customer 2019s inability to meet its financial obligations , a specific reserve is recorded against amounts due to reduce the net recognized receivable to the amount reasonably expected to be collected .
- `post-text-9` (post_text[9]): inventories accounted for on a lifo basis consist of purchased product and inventory manufactured at the company 2019s heritage u.s .

**Original gold annotations:**

```json
{
  "table_8": "( amounts in millions ) the total other accrued liabilities of 2012 is $ 247.9 ; the total other accrued liabilities of 2011 is $ 255.9 ;",
  "table_1": "( amounts in millions ) the income taxes of 2012 is $ 19.6 ; the income taxes of 2011 is $ 11.7 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 097. [train] `ETR/2004/page_159.pdf-1`

**Question:** what is the growth rate in net revenue in 2004 for entergy arkansas inc.?

**Mapped positives:**

- `table-row-1` (table[1]): 2003 net revenue | ( in millions ): $ 998.7
- `table-row-4` (table[4]): 2004 net revenue | ( in millions ): $ 978.4

**Five negative candidates:**

- `pre-text-6` (pre_text[6]): following is an analysis of the change in net revenue comparing 2004 to 2003. .
- `pre-text-0` (pre_text[0]): entergy arkansas , inc .
- `post-text-1` (post_text[1]): deferred fuel cost revisions decreased net revenue due to a revised estimate of fuel costs filed for recovery at entergy arkansas in the march 2004 energy cost recovery rider , which reduced net revenue by $ 11.5 million .
- `table-row-0` (table[0]): | ( in millions )
- `pre-text-3` (pre_text[3]): 2003 compared to 2002 net income decreased $ 9.6 million due to lower net revenue , higher depreciation and amortization expenses , and a higher effective income tax rate for 2003 compared to 2002 .

**Original gold annotations:**

```json
{
  "table_1": "the 2003 net revenue of ( in millions ) is $ 998.7 ;",
  "table_4": "the 2004 net revenue of ( in millions ) is $ 978.4 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 098. [train] `EW/2014/page_35.pdf-1`

**Question:** what was the 5 year cumulative total return for the period ending 2014 for edwards lifesciences corporation?

**Mapped positives:**

- `table-row-1` (table[1]): edwards lifesciences | 2010: $ 186.16 | 2011: $ 162.81 | 2012: $ 207.65 | 2013: $ 151.43 | 2014: $ 293.33
- `pre-text-1` (pre_text[1]): the cumulative total return listed below assumes an initial investment of $ 100 on december 31 , 2009 and reinvestment of dividends .

**Five negative candidates:**

- `table-row-3` (table[3]): s&p 500 healthcare equipment index | 2010: 96.84 | 2011: 102.07 | 2012: 120.66 | 2013: 153.85 | 2014: 194.33
- `table-row-2` (table[2]): s&p 500 | 2010: 115.06 | 2011: 117.49 | 2012: 136.30 | 2013: 180.44 | 2014: 205.14
- `pre-text-0` (pre_text[0]): 12feb201521095992 performance graph the following graph compares the performance of our common stock with that of the s&p 500 index and the s&p 500 healthcare equipment index .
- `table-row-0` (table[0]): total cumulative return | 2010 | 2011 | 2012 | 2013 | 2014
- `post-text-0` (post_text[0]): .

**Original gold annotations:**

```json
{
  "table_1": "total cumulative return the edwards lifesciences of 2010 is $ 186.16 ; the edwards lifesciences of 2011 is $ 162.81 ; the edwards lifesciences of 2012 is $ 207.65 ; the edwards lifesciences of 2013 is $ 151.43 ; the edwards lifesciences of 2014 is $ 293.33 ;",
  "text_1": "the cumulative total return listed below assumes an initial investment of $ 100 on december 31 , 2009 and reinvestment of dividends ."
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 099. [train] `UNP/2017/page_23.pdf-3`

**Question:** what was the percentage change in free cash flow from 2016 to 2017?

**Mapped positives:**

- `table-row-4` (table[4]): free cash flow | 2017: $ 2162 | 2016: $ 2253 | 2015: $ 524

**Five negative candidates:**

- `post-text-8` (post_text[8]): as prices fluctuate , there will be a timing impact on earnings , as our fuel surcharge programs trail increases or decreases in fuel price by approximately two months .
- `post-text-10` (post_text[10]): alternatively , lower fuel prices could likely have a negative impact on other commodities such as coal and domestic drilling-related shipments. .
- `pre-text-5` (pre_text[5]): gross-ton miles increased 5% ( 5 % ) , which also drove higher fuel expense .
- `post-text-6` (post_text[6]): we again could see volatile fuel prices during the year , as they are sensitive to global and u.s .
- `post-text-5` (post_text[5]): f0b7 fuel prices 2013 fuel price projections for crude oil and natural gas continue to fluctuate in the current environment .

**Original gold annotations:**

```json
{
  "table_4": "millions the free cash flow of 2017 is $ 2162 ; the free cash flow of 2016 is $ 2253 ; the free cash flow of 2015 is $ 524 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.

## 100. [train] `SWKS/2011/page_112.pdf-1`

**Question:** what is the net change amount of unrecognized tax benefits for the given period?

**Mapped positives:**

- `table-row-5` (table[5]): balance at september 30 2011 | $ 19900: $ 32136

**Five negative candidates:**

- `table-row-0` (table[0]): balance at october 1 2010 | $ 19900
- `post-text-2` (post_text[2]): for california and iowa , the company has open tax years dating back to fiscal year 2002 due to the carry forward of tax attributes .
- `table-row-2` (table[2]): increases based on positions related to current year | $ 19900: 11334
- `post-text-8` (post_text[8]): 11 .
- `post-text-15` (post_text[15]): the company 2019s second amended and restated certificate of incorporation provides that , unless otherwise determined by the company 2019s board of directors , no holder of common stock has any preemptive right to purchase or subscribe for any stock of any class which the company may issue or sell .

**Original gold annotations:**

```json
{
  "table_5": "balance at october 1 2010 the balance at september 30 2011 of $ 19900 is $ 32136 ;"
}
```

**Mapping check:** PASS — every annotation maps to the displayed positive ID.
