# monte ideas

## Reason Behind the Name

monte is named that for several reasons.

* One of my first experiences with highly parallel computing was my freshman year when we learned to do monte carlo simulations to calculate sqrt(2) and to compare runtimes for different amounts of points. I wanted to push my computer to go faster, calculate sqrt(2) to higher precision in less time. I found a MATLAB library that enabled parallel computing on the GPU and the syntax didn't look so bad so I tried it and increased the number of points I could run in 60 seconds by 1000x. It felt amazing and pushed me to go further into software.
* monte is a card game, a game of chance. this project originally started off as a DIY stock trading backtester with custom features. If you look at the really old commits (~commit number 300 is the end I think?), I had built a whole python package for my friends and I to use for backtesting different algorithms. I wanted to remind myself that the stock market is risky, and is a game of chance in its own way. monte was a warning that what we were doing was too risky for me to invest real money in.
* Pandas and Polars both have bears as their logo. Ours is named Wojtek, after a real-life bear that fought alongside the Polish in WWII. He helped at the Battle of Monte Cassino by moving ammunition with the soldiers. I liked the [monte <-> bear] connection so that was part of it.

## Random ideas

* You can replay data and then you can either stop, use predicted/forecasted data, or use live data being streamed from somewhere
* Turn monte into a generalized dataset replay package
* Rust, Python, and R support
* Add datasets to a hash map and increment all of the datasets at the same time
* Have a community poll that serves as public data collection for a public dataset
* Future language support: scala/julia? have to wait for Polars to support them (hint hint 😁)
* Don't worry about LazyFrames, they are an intermediate step that we don't need to support as an argument
* The Rust API should only use dataframes as a fundamental unit but make the Python API work with both DataFrames and Series
