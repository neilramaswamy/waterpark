# Waterpark: A playground for watermarks

Unfortunately, I can't motivate and explain watermarks here, since that's an entire topic in and of itself. If you're not already familiar with watermarks, please read [this blog post](https://www.databricks.com/blog/2022/08/22/feature-deep-dive-watermarking-apache-spark-structured-streaming.html), and come back.

Also, there are quiz questions/exercises at the end of the README, if you want a challenge :)

## Traditional watermark delays

Most systems these days compute watermarks based on a simple heuristic: they find the largest event-time up until some point (in Structured Streaming, for example, until the end of a batch), and then they subtract off a _watermark delay_ from that event-time. The resulting difference is your watermark.

Let's do an example. Suppose we receive a record with event-time `15`. If we know a priori that the maximum delay that the upstream processors could introduce is `5`, then the _earliest_ time at which that record could have been sent is `10`. As such, `10` would be our watermark. If we receive a record with timestamp less than `10`, we ignore it. The benefit to this scheme is that we can complete aggregates that happen before `10`, since we won't let any more records through with event-time less than 10.

This general approach is fairly reasonable. But what's _not_ reasonable is assuming that people know a priori the maximum delay of their upstream processors. Ideally, your streaming engine would be able to _infer_ what this delay should be, satisfying some minimum correctness threshold you set ("I want each aggregate to contain about 90% of the events for that window.")

## Statistical watermarking

Statistical watermarking has been discussed before primarily in literature in which Tyler Akidau is the first author. This project does not yet attempt to go into the details of how one would implement statistical watermarking. Rather, it aims to _demonstrate_ the relationship between delay distributions and aggregate correctness

For our purposes in the streaming world, the processing-time of an event is the record's event-time, _plus_ a delay random variable coming from some delay distribution `D`. The maximum delay of our watermark is the 100th percentile of this distribution `D`. Naturally, if we wait `p100(D)` time units, we'll never accidentally drop an element, since we wait for every one to arrive.

But waiting for the 100th percentile of the underlying distribution is too strict: in the real-world, the internet can introduce an unbounded amount of delay on a packet, so you'd be literally waiting forever if you waited for `p100(InternetDistribution)`. So instead of setting our watermark delay to be the _maximum_ possible delay, what if we set it to be the 90th percentile delay? Then, we'd receive 90% of events in our aggregates. Here's the main point:

**If we set our watermark delay to be the `p`th percentile of the underlying distribution, we'll end up waiting for `p`% of events before closing aggregates—our original goal!**

Again: this project does not go into implementation detail of how you'd implement this scheme. Rather, it provides a simulator where you can convince yourself of this fact.

## How to play in the Waterpark

### Configuration

You'll have to modify `sim.sh` to your liking, and then run that script. The supported parameters are below:

- `DISTRIBUTION`: `"gamma"`, `"exponential"`, `"uniform"`, `"constant"`
- `PARAMETERS`: comma-separated parameters to each. I know, this is a bit janky.
  - `gamma` takes in `<shape> <scale>`
  - `exponential` takes in `<rate>`
  - `uniform` takes in `<low> <high>`
  - `constant` takes in `<value>`.
- `WATERMARK_DELAY`: almost self-explanatory. However, this isn't the "maximum" delay anymore. It's the delay you'd like to experiment with. More on this below.
- `WATERMARK_SPEED`: the number of records to process before updating the watermark. Systems such as Structured Streaming update the watermark at discrete intervals, i.e. at the end of each batch. If you set this to be large, the watermark will move more slowly, since it is updated less frequently. This means that less records will be dropped. If you set this to be 1, then more records will be dropped.

You likely don't need to touch the following parameters. They're large enough for the resulting numbers to converge. But, if you really want to mess with them, `INPUT_RATE * DURATION` number of records are generated with event-times with a uniform distribution from `[0, DURATION]`.

- `INPUT_RATE`: the number of records per second to generate.
- `DURATION`: the number of seconds to generate records for.

### Simulation

After modifying these, just run `./sim.sh`. Results will take 5 seconds, since we simulate with several million events.

### A Simple Example

Suppose that the underlying delay distribution is `Unf(0 5)`. If we want to receive 60% of events, then we should make sure to wait 3 units of time. We modify the following parameters in `sim.sh`:

```sh
...

DISTRIBUTION="uniform"
PARAMETERS="0 5"

WATERMARK_DELAY="3"
WATERMARK_SPEED="100"

...
```

After running `./sim.sh`, you should see the following printed to your console:

```
(percentage_aggregated: 0.6092819)
```

Neat!

### A More Involved Example

Now let's say that we know that our delay distribution is `Exp(0.5)`. If we want 90% of the events, we can pass in `0.9` to the inverse CDF of `Exp(0.5)`. I don't know this off the top of my head, but [Wolfram Alpha does](https://www.wolframalpha.com/input?i=inverse+cdf+of+exponential%280.5%29). Passing `0.9` to that, we see that we should wait (i.e. our watermark delay should be) 4.61. Let's try that out in `sim.sh`:

```sh
...

DISTRIBUTION="exponential"
PARAMETERS="0.5"

WATERMARK_DELAY="4.61"
WATERMARK_SPEED="100"

...
```

After running `./sim.sh`, you should see the following printed to your console:

```
(percentage_aggregated: 0.9018373)
```

Yay!

### Homework questions

Here are some investigations you should try to perform:

1. Modify just the `WATERMARK_SPEED`. How does this affect the percentage of events aggregated?
2. Set the `WATERMARK_DELAY` to 0. Can you figure out what other parameter(s) to modify to make sure that about 100% of events are aggregated?
3. Without simulating this, if you set the `WATERMARK_DELAY` to be _less_ than the `p0` of your distribution, what do you expect will happen to the percentage of events that are aggregated?
4. Write some test cases for `waterpark.py`. Submit them as a pull request. How does it feel knowing that you just made a meaningful contribution to open-source software?
