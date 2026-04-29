Project X: Credit-Driven Equity Intelligence Agent

🎯 Objective
This repository studies the interplays between credit risk and equity pricing for individual companies. 

We adopt a credit-first approach to identify equity dislocation opportunities—situations where the equity market misprices a stock because it overlooks or misinterprets the credit-side signals such as credit risk, revolver usage, bank-provided flexibility, covenant structure, liquidity runway, and the company's overall debt stack. 

While the framework can surface both downside risk and upside potential, it is primarily designed to identify undervalued equity opportunities.

🧠 The "Credit-to-Equity" Thesis

For highly leveraged companies, credit risk can begin migrating into equity pricing when the financial leverage becomes elevated, often around 4.0x debt-to-EBITDA or higher. 
Signals such as weakening free cash flow, declining net income, increasing revolver usage, reduced liquidity availability, shrinking covenant headroom, or a near-term maturity wall should make investors to reassess the stock less as a simple claim on future earnings and more as a residual claim beneath a constrained capital stack.

In this framework, the key bridge is:
Equity value = Targeted Enterprise value − net debt − other senior claims
where:
Targeted EV = normalized EBITDA × **Exit multiple**
normalized EBITDA = normalized revenue * normalized EBITDA Margin
net debt = current net debt + future new debt - cumulative FCF used for debt payment
then 
Stock price = equity value / diluted shares outstanding

To obtain the exit mutliple, EV/EBITDA, one consider two approaches
1. Find the median EV/NTM EBITDA among industry peers and apply "growth and credit adjustment" 
2. Regress EV / LTM EBITDA on Debt / LTM EBITDA
    2.a. find the normalized EBITDA from ART
    2.b. find the exit multiple by plugging the companies-specific metrics.


A few things can counter the thesis
1. Business / Operation news can still overwhelm credit news
2. Market positioning and sentiment can distort short-term price action



Important credit inflection points include:

| Inflection point                      | Equity-market interpretation                                                   |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| Liquidity runway shortens             | Higher risk of emergency financing, asset sales, or restructuring              |
| Revolver availability declines        | Less flexibility to absorb cash burn                                           |
| Covenant headroom tightens            | Lenders gain more negotiating power                                            |
| Debt maturity approaches              | Refinancing risk becomes urgent                                                |
| Borrowing cost rises                  | Future free cash flow to equity declines                                       |
| Credit agreement is amended           | Could be positive if it buys time; negative if terms are punitive              |
| Debt exchange / refinancing announced | Could reduce default risk but increase dilution or transfer value to creditors |


| Metric    | What it tries to show                                |
| --------- | ---------------------------------------------------- |
| P/E       | How much investors pay for earnings                  |
| EV/EBITDA | How much investors pay for operating earnings        |
| P/S       | How much investors pay for revenue                   |
| P/B       | How much investors pay for book value                |
| FCF yield | How much free cash flow equity investors may receive |


1. Business / Operation news can still overwhelm credit news
| Business catalyst             | Why it can dominate                        |
| ----------------------------- | ------------------------------------------ |
| Better-than-expected earnings | EBITDA improves leverage and survival odds |
| Margin recovery               | Free cash flow outlook improves            |
| Strong demand                 | Refinancing confidence increases           |
| Asset sale at high valuation  | Deleveraging becomes easier                |
| New contract/customer win     | Enterprise value increases                 |
| Commodity price rebound       | Cash flow outlook improves                 |


2. Market positioning and sentiment can distort short-term price action
| Technical factor    | Impact                                                |
| ------------------- | ----------------------------------------------------- |
| High short interest | Positive credit news can trigger a squeeze            |
| Forced selling      | Stock can fall even before credit fundamentals worsen |
| Index deletion risk | Passive flows pressure stock                          |
| Retail speculation  | Equity may detach from fundamentals                   |
| Options activity    | Gamma/volatility can dominate short-term moves        |



🛠 Features & Agent Modules


📈 Roadmap