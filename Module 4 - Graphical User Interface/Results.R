# Raw SUS scores per participant
sus_scores20 <- c(
  92.5, 72.5, 85, 80, 80, 95, 85, 85, 77.5, 90,
  82.5, 80, 70, 90, 92.5, 57.5, 87.5, 87.5, 90, 85
)

n <- length(sus_scores20)
means <- numeric(n)
errors <- numeric(n)
ci_lower <- numeric(n)
ci_upper <- numeric(n)

# Calculate mean and 95% CI 
for (i in 2:n) {
  subset_scores <- sus_scores20[1:i]
  m <- mean(subset_scores)
  s <- sd(subset_scores)
  err <- qt(0.975, df = i - 1) * (s / sqrt(i))
  
  means[i] <- m
  errors[i] <- err
  ci_lower[i] <- m - err
  ci_upper[i] <- m + err
}

final_i <- n
cat(sprintf("Final Number of Participants: %d\n", final_i))
cat(sprintf("Final Mean SUS Score: %.2f\n", means[final_i]))
cat(sprintf("95%% Confidence Interval: [%.2f, %.2f]\n", ci_lower[final_i], ci_upper[final_i]))
cat(sprintf("Margin of Error: ±%.2f\n", errors[final_i]))

#####################################################################


# Calculate z-score for participant #16 (possible outlier)
x_16 <- sus_scores20[16]
mean_all <- mean(sus_scores20)
sd_all <- sd(sus_scores20)
z_16 <- (x_16 - mean_all) / sd_all

cat(sprintf("Participant #16 SUS Score: %.1f\n", x_16))
cat(sprintf("Mean SUS Score: %.2f\n", mean_all))
cat(sprintf("Standard Deviation: %.2f\n", sd_all))
cat(sprintf("Z-score for Participant #16: %.2f\n", z_16))



######################################################################
# Run one-sample t-test against benchmark of 80
t_result <- t.test(sus_scores20, mu = 80, alternative = "greater")

# Print result
print(t_result)

# Print p-value separately
cat("\nP-value:", round(t_result$p.value, 4), "\n")

######################################################################
# ANOVA: Compare SUS scores between early, middle, and late groups

# Create groups 1–7 (early participants), 8–14 (middle participants), 
# 15–20 (late participants)
group_labels <- factor(rep(c("Early", "Mid", "Late"), times = c(7, 7, 6)))

# Create a data frame for analysis
anova_data <- data.frame(
  Score = sus_scores20,
  Group = group_labels
)

# Run one-way ANOVA
anova_result <- aov(Score ~ Group, data = anova_data)

# Print ANOVA summary
cat("\n One-Way ANOVA Results \n")
summary(anova_result)


