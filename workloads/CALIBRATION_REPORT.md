# Workload descriptor and passage boundary

The three tree sizes were selected to exercise authentication paths of increasing depth while keeping the reference run feasible on an ordinary reviewer workstation. The event stream cycles deterministically through nine synthetic templates covering seven evidence-event classes.

The word “calibration” is retained in filenames required by the project structure. Scientifically, the inputs are externally informed synthetic descriptors rather than estimates of a clinical population, patient behaviour, physiological sampling distribution or production workload.

The retained full run executes `12 × (128 + 512 + 2048) = 32,256` events, `3 × 12 × 32 = 1,152` sampled receipt checks and `3 × 12 × 1 = 36` re-signed proof-path mutations. The raw rows, summaries, hardware profile and batch-merger provenance are distributed with the archive under a single run identifier. The passage results are bounded to the stated implementation, host and tree sizes.
