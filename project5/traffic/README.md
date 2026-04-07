# Traffic Sign Recognition - CS50 AI Project

A CNN that recognizes German traffic signs (43 categories) trained on the GTSRB dataset.

## Experimentation Process

I started with the basic two-layer CNN from the course but only got 96% accuracy. Adding a third conv layer with 128 filters and batch normalization pushed me to 98%. The biggest improvement came from swapping Flatten for GlobalAveragePooling2D - hit 99.2% just from that change. Less parameters and apparently better for this problem.

Adding 1x1 convolutions after each conv layer got me to 99.6% but training slowed down noticeably. What didn't work was making the dense layer bigger than 256 neurons - the model overfit hard, with training at 99.9% but test stuck at 98.5%. Label smoothing (0.1) helped with generalization but made the loss values look weirdly high, which confused me at first.

The main thing I learned was watching the gap between training and test accuracy. When the gap grew past 0.5% I knew I was overfitting. My final model (32→64→128 filters with 1x1 convs, batch norm, global pooling, dropout 0.5) got 99.62% test accuracy. Good enough for traffic signs but 30x30 pixels feels too small for signs with tiny text.