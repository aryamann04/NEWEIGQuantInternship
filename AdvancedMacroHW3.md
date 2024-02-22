Advanced Macroeconomics Homework 3
================
2024-02-22

# Problem 1: Summarizing the Data

## 1(a): Summary statistics

``` r
data <- read.table("/Users/aryaman/Downloads/MRW_2015.csv", header = TRUE, sep = "\t")

# Drop major oil producing countries from the data set
data <- data[data$oil == 0, ]

# Create a simple function to get the desired statistics 
stat <- function(x) {
  result <- list(
    Mean = round(mean(x),4),
    Median = round(median(x),4),
    Sd = round(sd(x),4),
    Min = round(min(x),4),
    Max = round(max(x),4)
  )
  return(result)
}
data["delta_ln_YL"] <- log(data$rgdpe2015 / data$rgdpe1990)

stats_1990 <- sapply(data[, c("rgdpe1990", "popgrowth1990", "savingsrate1990", 
                "schooling1990")], stat)

stats_2015 <- sapply(data[, c("rgdpe2015", "popgrowth2015", "savingsrate2015", 
                "schooling2015", "delta_ln_YL")], stat)

knitr::kable(stats_1990, caption = "Summary Statistics 1990", format = "latex",
             position = "h")
```

``` r
knitr::kable(stats_2015, caption = "Summary Statistics 2015 and Delta Y/L", 
             format = "latex", position = "h")
```

## 1(b): Scatter plots

### 1(b)(i):

``` r
scatter_plot_1990 <- ggplot(data, aes(x = log(savingsrate1990) 
  - log(popgrowth1990 + 0.02 + 0.03), y = log(rgdpe1990))) +
  geom_point() +
  labs(title = "Solow Growth Scatter Plot: 1990", 
       x = "ln(s) - ln(n + g + delta)", y = "ln(Y/L)")

scatter_plot_2015 <- ggplot(data, aes(x = log(savingsrate2015) 
  - log(popgrowth2015 + 0.02 + 0.03), y = log(rgdpe2015))) +
  geom_point() +
  labs(title = "Solow Growth Scatter Plot: 2015", 
       x = "ln(s) - ln(n + g + delta)", y = "ln(Y/L)")

plot(scatter_plot_1990)
```

![](AdvancedMacroHW3_files/figure-gfm/unnamed-chunk-2-1.png)<!-- -->

``` r
plot(scatter_plot_2015)
```

![](AdvancedMacroHW3_files/figure-gfm/unnamed-chunk-2-2.png)<!-- -->

### 1(b)(iii): Economic Theory

The Solow Growth Model postulates that in the steady-state, capital per
effective unit of labor should satisfy
$$k^* = \left( \frac{s}{n+g+\delta} \right)^{\frac{1}{1-\alpha}}$$ and
output per capita $$\frac{Y_t}{L_t} = A_t(k^*)^\alpha$$ Taking logs, we
arrive to the relation
$$\ln{\frac{Y}{L}} = \ln{A_0} + g \cdot t + \frac{\alpha}{1-\alpha}\ln{s} - 
\frac{\alpha}{1-\alpha}\ln{(n + g+\delta)}$$ From this, we can
hypothesize the linear relationship
$$\ln{\frac{Y}{L}} = a + \frac{\alpha}{1-\alpha}(\ln{s} - \ln{(n+g+\delta)}) + \epsilon$$
Thus, the Solow Growth Model predicts that our scatter plots should
generally exhibit a positive linear relationship between $\ln{Y/L}$ and
$\ln{s} - \ln{(n+g+\delta)}$. This relationship should have the
approximate slope of $\alpha/(1-\alpha)$, implying that, under the Solow
model, a 1% increase in $\ln{s}$ or 1% decrease in $\ln{(n+g+\delta)}$
predicts a $\alpha/(1-\alpha)$ percent increase in per capita output. We
can observe this generally positive, direct relationship between
$\ln{s} - \ln{(n+g+\delta)}$ and $\ln{\frac{Y}{L}}$ in the scatter plot.

# Problem 2: Regressing Y/L on Savings and Population Growth, 1990

We will aim to estimate the regression
$$\ln{Y/L} = \beta_0 + \beta_1\ln{(s)}
+ \beta_2\ln{(n + g + \delta)} + \epsilon$$ where we assume that
$g + \delta = 0.05$.

``` r
model_1990 <- lm(log(rgdpe1990) ~ log(savingsrate1990) + log(popgrowth1990 + 
                0.05), data = data)

tidy_model_1990 = tidy(model_1990)

kable(tidy_model_1990, caption = "Regression Results - 1990", 
      format = "latex", position = "h")
```

``` r
r2 <- summary(model_1990)$adj.r.squared
n <- length(model_1990$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.4234

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

## 2(a): Comparing coefficients to Mankiw, Romer, Weil

Our regression yielded a coefficient $\beta_1 = 1.23$, slightly lower
than 1.42 estimated by Mankiw, Romer, and Weil with a similar standard
error of 0.17 compared to MRW’s 0.14. The p-value for $\ln{s}$ is
approximately 0, indicating a high level of statistical significance.

We also observe a coefficient value $\beta_2 = -1.41$, lower in absolute
magnitude than MRW’s estimate of -1.97. The standard error of this
regression 0.69, slightly higher than MRW’s standard error of 0.56. The
p-value corresponding to $\ln{(n+g+\delta)}$ in our regression was 0.04,
which is significant at the $p=0.05$ level. We can conclude that our
results are generally similar to those of MRW.

## 2(b): Discussion of coefficients in the Solow Model

We first observe that $\beta_1$ and $\beta_2$ are almost equal in
magnitude and opposite in signs, which is what the Solow Model predicts.
Specifically, the model predicts that
$$\beta_1 = -\beta_2 = \frac{\alpha}{1-\alpha}$$ Thus, we can back out a
value for the estimated average capital share, $\alpha$, across the
countries in the data set. Using $\beta_1 = 1.23$, we get a value of
$\alpha = 0.552$. This is still significantly higher than measured
estimates of the capital share placing it at around $1/3$, but lower
than MRW’s estimate of 0.6. With $\beta_2 = 1.41$, we get a capital
share estimate of $\alpha = 0.585$. This is not too far from our capital
share estimate using $\beta_1$. We can conclude that our regression is
relatively consistent with the Solow Model, but significantly
overestimates the capital share like MRW’s regression.

# Problem 3: Effect of Schooling, 1990

We will augment the previous regression by considering schooling:
$$\ln{Y/L} = \beta_0 + \beta_1\ln{(s)} + \beta_2\ln{(n + g + \delta)}
+ \beta_3\ln{(H)} + \epsilon$$ where $H$ represents the schooling
variable, represented in the data as average years of schooling.

``` r
school_model_1990 <- lm(log(rgdpe1990) ~ log(savingsrate1990) + 
                  log(popgrowth1990 + 0.05) + log(schooling1990), data = data)

tidy_school_model_1990 <- tidy(school_model_1990)

kable(tidy_school_model_1990, caption = "Regression Results with Schooling
      - 1990", format = "latex", position = "h")
```

``` r
r2 <- summary(school_model_1990)$adj.r.squared
n <- length(school_model_1990$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.6162

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

## 3(a): Schooling Coefficient

The regression estimates a value of $\beta_3 = 1.05$ corresponding to
the schooling variable. Thus, the regression estimates that if a
country’s average log years of schooling increases by one year, log per
capita output would increase by 1.05. This makes intutive sense because
we can expect higher schooling rates to increase human capital and thus
making workers more productive on average, increasing per capita output.

## 3(b): Effect on Coefficients for Savings and Population Growth

After running this regression, our coefficient $\beta_1$ corresponding
to the savings rate decreased significantly to 0.59 from 1.23. The
coefficient $\beta_2$ corresponding to $\ln{(n+g+\delta)}$ went from
-1.41 to 0.17, contradicting what the Solow Model predicts since the
coefficient should be negative and somewhat similar in magnitude to
$\beta_1$. However, the p-value of $\beta_2$ is 0.79, which is far too
high to accept as statistically significant. Thus, after adding the
schooling variable, the degree to which the savings rate and population
growth rate affected log per capita output decreased.

## 3(c): Discussion

Our traditional Solow Model has now been augmented to include a measure
for human capital, i.e. our production function is now
$$Y_t = K^\alpha_tH^\gamma_t(A_tL_t)^{1-\alpha-\gamma}$$

Using the same method of logs to arrive at our regression equation, we
see that our model predicts that our coefficients for $\ln{(s)}$,
$\ln{(n+g+\delta)}$, and $\ln{H}$ will be
$$\beta_1 = -\beta_2 = \frac{\alpha}{1-\alpha}$$
$$\beta_3 = \frac{\gamma}{1-\alpha}$$ Let us repeat a similar process as
we did in 2(b) to back out values for the capital share $\alpha$. Using
$\beta_1 = 0.59$, we arrive at a plausible capital share estimate of
0.37, which is much closer to the measured capital share value of $1/3$.
However, if we use $\beta_2 = 0.17$, we get $\alpha = -0.20$, which is
an impossible value since $0 < \alpha < 1$ must be satisfied.

In spite of this clear contradiction of the model, we can estimate the
human capital share by using our capital share estimate using $\beta_1$.
Specifically, $$\beta_3 = \frac{\gamma}{1-\alpha}$$
$$\implies \gamma = \beta_3(1-\alpha)$$ $$= 0.66$$

This is a plausible value since $0 < \gamma < 1$, but it likely is
overestimated by this model. Further, we notice that our estimates for
the savings rate coefficient is similar to that of MRW, who calculated
$\beta_1 = 0.69$. However, the schooling coefficient we observe is far
higher than MRW’s estimate of $\beta_3 = 0.66$. The population growth
coefficient calculated in our regression is significantly different to
that of MRW, who calculated a negative value of $\beta_2 = -1.73$
compared to our $0.16$.

## 3(d): Restricting Coefficient Signs

In order to ensure that the coefficients corresponding to the savings
rate and population growth term are equal in magnitude and opposite in
sign, i.e. in our previous regression we want to force
$\beta_1 = -\beta_2$, we can modify our regression equation to combine
the terms for savings rate and population growth.
$$\ln{Y/L} = \gamma_0 + \gamma_1\ln{s} - \gamma_1\ln{(n+g+\delta)} + \gamma_2\ln{H}$$
$$\implies \ln{Y/L} = \gamma_0 + \gamma_1\ln{\left(\frac{s}{n+g+\delta}\right)} + \gamma_2\ln{H}$$

``` r
restricted_model_1990 <- lm(log(rgdpe1990) ~ 
                   log(savingsrate1990/(popgrowth1990 + 0.05)) + 
                   log(schooling1990), data = data)

tidy_restricted_model_1990 <- tidy(restricted_model_1990)

kable(tidy_restricted_model_1990, caption = "Restricted Regression Results with 
      Schooling - 1990", format = "latex", position = "h")
```

``` r
r2 <- summary(restricted_model_1990)$adj.r.squared
n <- length(restricted_model_1990$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.6137

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

Here, the coefficient $\gamma_1 = 0.556$ is significant at the $p<0.002$
level. This indicates that if we performed our inital regression with
schooling, i.e. 
$$\ln{Y/L} = \beta_0 + \beta_1\ln{(s)} + \beta_2\ln{(n + g + \delta)}
+ \beta_3\ln{(H)} + \epsilon$$ but restricted it such that
$\beta_1 = -\beta_2$ as the Solow model predicts, then our OLS model
estimates $\beta_1 = \gamma_1 = 0.556$ and
$\beta_2 = -\gamma_1 = -0.556$. The coefficient on the schooling
variable is $\gamma_2 = 0.999$ which is a slight decrease from the
unrestricted regression which yielded $\beta_3 = 1.05$. Our
corresponding capital and human capital shares are $$\alpha = 0.357$$
$$\gamma = 0.68$$ Both estimates are somewhat reasonable, but both are
overestimated. The capital share is closer to the measured value, but it
is highly likely that the share of output attributed to $H_t$ is less
than 0.68.

# Problem 4: Regressing Y/L on Savings, Population Growth, and Schooling, 2015

We will first approximate the regression omitting schooling:
$$\ln{(Y/L)}_{2015} = \beta_0 + \beta_1\ln{(s)}
+ \beta_2\ln{(n + g + \delta)} + \epsilon$$

``` r
model_2015 <- lm(log(rgdpe2015) ~ log(savingsrate1990) + log(popgrowth1990 
              + 0.05), data = data)

tidy_model_2015 <- tidy(model_2015)

kable(tidy_model_2015, caption = "Regression Results - 2015", 
      format = "latex", position = "h")
```

``` r
r2 <- summary(model_2015)$adj.r.squared
n <- length(model_2015$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.3987

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

We notice that our estimate for the savings rate coefficient is 1.13,
similar to our 1990 value of 1.23. The estimate for the population
growth increased in magnitude in our 2015 results from -1.41 to -2.08.
This suggests that the 2015 data shows a steeper inverse relationship
between the population growth term and per capita output when compared
to the 1990 data. We also notice that the regression results in 2015 are
not as consistent with the Solow model as the 1990 regression is since
the savings rate and population growth terms ($\beta_1 = 1.13$ while
$\beta_2 = -2.08$ in 2015) do not have approximately the same magnitude
and opposite signs, as the model predicts.

Next, we will estimate the regression
$$\ln{(Y/L)}_{2015} = \beta_0 + \beta_1\ln{(s)} + \beta_2\ln{(n + g + \delta)}
+ \beta_3\ln{(H)} + \epsilon$$

``` r
school_model_2015 <- lm(log(rgdpe2015) ~ log(savingsrate2015) + 
                    log(popgrowth2015 + 0.05) + log(schooling2015), data = data)

tidy_school_model_2015 <- tidy(school_model_2015)

kable(tidy_school_model_2015, caption = "Regression Results with Schooling
      - 2015", format = "latex", position = "h")
```

``` r
r2 <- summary(school_model_2015)$adj.r.squared
n <- length(school_model_2015$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.7273

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

Our coefficient for schooling in 2015 of 1.81 is significantly higher
than the 1990 coefficient for schooling of 1.04, indicating that a
percent increase in log average schooling increases log per capita
output to a greater extent in 2015 than in 1990. The 2015 estimate for
the savings rate is also significantly higher with a value of 1.07
compared to 0.59 in 1990. The population growth term coefficient has an
insignificant p-value in both the 1990 and 2015 regression.

For the restricted regression, we will similarly estimate
$$\ln{(Y/L)}_{2015} = \gamma_0 + \gamma_1\ln{\left(\frac{s}{n+g+\delta}\right)} + \gamma_2\ln{H}$$

``` r
restricted_model_2015 <- lm(log(rgdpe2015) ~ 
                          log(savingsrate2015/(popgrowth2015 + 0.05))
                          + log(schooling2015), data = data)

tidy_restricted_model_2015 <- tidy(restricted_model_2015)

kable(tidy_restricted_model_2015, caption = "Restricted Regression Results with 
      Schooling - 2015", format = "latex", position = "h")
```

``` r
r2 <- summary(restricted_model_2015)$adj.r.squared
n <- length(restricted_model_2015$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.721

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

The observed restricted coefficient for the savings rate is
$\gamma_1 = 0.93$. Correspondingly, the coefficient for population
growth $-\gamma_1 = -0.93$. The magnitude of this restricted coefficient
is almost two times larger than that of the 1990 regression restricted
coefficient of $0.56$. The restricted coefficient also has a signficant
p-value as it did in the 1990 data. The coefficient on schooling
increased significantly from 1.00 in 1990 to 1.73 in 2015. The
corresponding capital and human capital share is $$\alpha = 0.48$$
$$\gamma = 0.90$$ While both are overestimates, the capital share is
somewhat close to the measured value. However, a human capital share of
0.9 is far too high and violates the fact that $\alpha + \gamma < 1$.
Thus, the 2015 model may overestimate the effect of schooling on per
capita output more than the 1990 model does.

# Problem 5: Conditional and Unconditional Convergence in Living Standards

## 5(a): Unconditional Convergence Scatter Plot

``` r
conv <- ggplot(data, aes(x = log(rgdpe1990), y = delta_ln_YL)) +
  geom_point() +
  labs(title = "Unconditional Convergence : Delta ln(Y/L) vs. ln(Y/L) in 1990", 
  x = "ln(Y/L) in 1990", y = "Delta ln(Y/L)")

print(conv)
```

![](AdvancedMacroHW3_files/figure-gfm/unnamed-chunk-9-1.png)<!-- -->

Unconditional convergence is the hypothesis that a country with a high
current per capita output will expect slower future growth in per capita
output compared to a country with a currently lower per capita output.
In the scatter plot, we observe a very slight and weak negative linear
relationship between log per capita output in 1990 and the change in log
per capita output from 1990 to 2015 across different countries. The
scatter plot shows little evidence for unconditional convergence since
no strong linear relationship is present.

## 5(b): Regressing for Unconditional Convergence

We aim to estimate
$$\Delta\ln{Y/L} = \beta_0 + \beta_1\ln{Y/L}_{1990} + \epsilon$$

``` r
model_uncond_conv <- lm(delta_ln_YL ~ log(rgdpe1990), data = data)

tidy_model_uncond_conv <- tidy(model_uncond_conv)

kable(tidy_model_uncond_conv, caption = "Unconditional Convergence:
      Regression Results", format = "latex", position = "h")
```

``` r
r2 <- summary(model_uncond_conv)$adj.r.squared
n <- length(model_uncond_conv$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.0118

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

The coefficient is estimated as $\beta_1 = -0.06$. While this slope is
negative, it is very close to zero, implying that a given difference in
1990 per capita output between two countries has a relatively small
impact on the difference between their growth in living standards across
the following 25 years. The slope is also not statistically significant
with a p-value of 0.167. This is consistent with MRW’s regression as
their estimated coefficient of 0.09 is also close to zero and has an
$R^2$ value close to zero as well. Thus, like MRW, we conclude that our
sample does not show convincing evidence of unconditional convergence,
i.e.  poor countries do not necessarily tend to grow faster than richer
countries.

## 5(c): Regressing for Conditional Convergence

To investigate for conditional convergence, our regression will estimate
$$\Delta\ln{Y/L} = \beta_0 + \beta_1\ln{Y/L}_{1990} + \beta_xX + \epsilon$$

We will choose the conditioning variable $X$ to be each savings rate,
population growth, and schooling. After running each of these three
separate regressions, we will include all three and estimate the above
regression with $X_1 = \text{savingsrate}$, $X_2 = \text{popgrowth}$,
and $X_3 = \text{schooling}$.

#### 5(c)(1): Convergence, Conditioned on Savings Rate

$$\Delta\ln{Y/L} = \beta_0 + \beta_1\ln{Y/L}_{1990} + \beta_{X_1}X_1 + \epsilon$$
where $X_1$ is the conditioning variable for savings rate.

``` r
model_cond_savings <- lm(delta_ln_YL ~ log(rgdpe1990) + 
                          log(savingsrate1990), data = data)

tidy_model_cond_savings <- tidy(model_cond_savings)

kable(tidy_model_cond_savings, caption = "Convergence Conditioned on Savings:
      Regression Results", format = "latex", position = "h")
```

``` r
r2 <- summary(model_cond_savings)$adj.r.squared
n <- length(model_cond_savings$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  -9e-04

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

From the high p-values and coefficients close to zero, we see that
savings rate is not an informative conditioning variable for
convergence.

#### 5(c)(2): Convergence, Conditioned on Population Growth

$$\Delta\ln{Y/L} = \beta_0 + \beta_1\ln{Y/L}_{1990} + \beta_{X_2}X_2 + \epsilon$$
where $X_2$ is the conditioning variable for population growth.

``` r
model_cond_popgrowth <- lm(delta_ln_YL ~ log(rgdpe1990) + log(popgrowth1990 + 0.05), 
                           data = data)

tidy_model_cond_popgrowth <- tidy(model_cond_popgrowth)

kable(tidy_model_cond_popgrowth, caption = "Convergence Conditioned on
     Population Growth: Regression Results", 
     format = "latex", position = "h")
```

``` r
r2 <- summary(model_cond_popgrowth)$adj.r.squared
n <- length(model_cond_popgrowth$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.0593

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

While the coefficient on population growth is negative and significantly
away from zero at the $p<0.05$ significance level, the coefficient on
1990 living standards is still close to zero with a relatively high
p-value. Population growth thus may not be the most informative
conditioning variable to investigate convergence.

#### 5(c)(3): Convergence, Conditioned on Schooling

$$\Delta\ln{Y/L} = \beta_0 + \beta_1\ln{Y/L}_{1990} + \beta_{X_3}X_3 + \epsilon$$
where $X_3$ is the conditioning variable for schooling.

``` r
model_cond_schooling <- lm(delta_ln_YL ~ log(rgdpe1990) + log(schooling1990), 
                           data = data)

tidy_model_cond_schooling <- tidy(model_cond_schooling)

kable(tidy_model_cond_schooling, caption = "Convergence Conditioned on
     Schooling: Regression Results", 
     format = "latex", position = "h")
```

``` r
r2 <- summary(model_cond_schooling)$adj.r.squared
n <- length(model_cond_schooling$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.1268

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

In this regression, we see the greatest evidence for conditional
convergence. The coefficient on 1990 living standards is negative and
significant, and the coefficient on 1990 schooling is positive and
significant. This suggests that the sample of countries show convincing
evidence of convergence if they all had the same level of schooling.

#### 5(c)(4): Combined Conditional Convergence

We will now estimate the regression combining all three of our
conditioning variables, i.e:
$$\Delta\ln{Y/L} = \beta_0 + \beta_1\ln{Y/L}_{1990} + \beta_{X_1}X_1
+ \beta_{X_2}X_2 + \beta_{X_3}X_3 + \epsilon$$

``` r
model_cond_combined <- lm(delta_ln_YL ~ log(rgdpe1990) + log(savingsrate1990) +     
                       log(popgrowth1990 + 0.05) + log(schooling1990), data = data)

tidy_model_cond_combined <- tidy(model_cond_combined)

kable(tidy_model_cond_combined, caption = "Convergence Conditioned on
     Savings, Pop Growth, and Schooling: Regression Results", 
     format = "latex", position = "h")
```

``` r
r2 <- summary(model_cond_combined)$adj.r.squared
n <- length(model_cond_combined$residuals)
cat(paste("Adjusted R-squared: ", round(r2, 4), "\n"))
```

    ## Adjusted R-squared:  0.1245

``` r
cat(paste("Sample Size: ", n, "\n"))
```

    ## Sample Size:  80

### 5(c)(i): Discussion

As observed in the regression in section $5(\text{b})$, there the sample
does not follow unconditional convergence in living standards, a
conclusion also drawn by MRW. We notice this from the coefficient being
assigned negligible weight by the regression and its statistical
insignificance inferred by the p-value.

The Solow Model does not predict unconditional convergence, it rather
shows that a country will converge to its steady-state living standards
which is determined by factors such as the savings rate and population
growth. Therefore, the Solow model does predict convergence conditioned
on these variables. This is supported by the regression we ran in
section $5(\text{c})(4)$.

We first notice that the savings rate coefficient $\beta_{X_1} = -0.05$
is negligible and has an insignificant p-value. Moreover, while the
population growth term $\beta_{X_2} = -0.44$ does have significant
negative weight, its p-value suggests the relationship is not
statistically significant.

The regression allocates a significant positive weight of
$\beta_{X_3} = 0.34$ to the schooling rate in determining growth in
living standards. Essentially, this suggests that if countries did not
vary in their schooling rates, there would be strong evidence for
convergence in living standards across the sample of countries from
1990-2015.

The coefficient on 1990 living standards is negative and significant,
corroborating the Solow model’s prediction of conditional convergence.
In their regression, MRW also find significant evidence for convergence
in living standards when conditioned on saving and population growth,
and even more when conditioned on saving, population growth, and human
capital.

Similar to our regression, MRW estimated a negative coefficient for
population growth but with a high standard error. Further, MRW also
estimated a significant, positive coefficient for schooling. However,
MRW found a much more significant relationship with the savings rate
than we did, obtaining a coefficient of 0.524 compared to our $-0.05$.

### 5(c)(ii): Schooling Variable

Considering all of the previous regressions, the schooling variable
seems to be the most informative conditioning variable for conditional
convergence. In our combined regression, the schooling coefficient was
the only estimate with a statistically significant p-value.

### (5)(c)(iii): Speed of Convergence

As MRW show, the speed of convergence to steady-state is given by

$$\frac{d\ln{y(t)}}{dt} = \lambda(\ln{y^*} - \ln{y(t)})$$

Where $y^*$ represents the steady-state level of income per effective
unit of labor, and $$\lambda = (n+g+\delta)(1-\alpha-\gamma)$$ is the
convergence rate. Here, $\alpha$ represents the capital share of output,
while $\gamma$ human capital share of output.

Our coefficient for the savings rate is unsuitable to use to estimate
the capital share since it is negative which will lead to a negative
capital share estimate. Thus, if we use the population growth
coefficient $\beta_{X_2} = -0.444$, we get an average capital share
estimate of$$\alpha = \frac{\beta_{X_2}}{1+\beta_{X_2}}= 0.307$$ for the
countries in the sample. Using that to calculate the human capital
share, we arrive at the estimate
$$\gamma = \beta_{X_3}(1-\alpha) = 0.238$$ These are both reasonable
estimates and satisfy $\alpha+\gamma < 1$.

To calculate $\lambda$, we now only need an estimate for population
growth, $n$. We can estimate this as the average population growth rate
in 1990 for the countries in the sample.

``` r
mean(data$popgrowth1990)
```

    ## [1] 0.02272569

Finally, substituting the assumption that $g+\delta = 0.05$, we solve
$$\lambda = (n+g+\delta)(1-\alpha-\gamma)$$
$$= (0.023 + 0.05)(1-0.307-0.238)$$ $$=0.0332$$

This is significantly higher than the MRW’s estimated implied
convergence rate of 0.0137. To calculate how many years it would take
for the economies to converge halfway to steady-state on average, we
observe that

$$\frac{d\ln{y(t)}}{dt} = \lambda(\ln{y^*} - \ln{y(t)})$$

can be solved as a differential equation for $y(t)$. We then can solve
for $t$ $$0.5 = e^{-\lambda t}$$
$$t = \ln{(0.5)} \cdot \frac{1}{-0.0332} = 20.88$$ Thus, it would take
approximately 21 years for the economies in this sample to converge
halfway to steady state.

Over ten years, in logs, approximately $\lambda \cdot t = 0.332$ of the
gap in living standards is closed.
