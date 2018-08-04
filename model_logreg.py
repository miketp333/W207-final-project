
# coding: utf-8

# # Logistic Regression Notebook
# [Return to project overview](final_project_overview.ipynb)
# 
# ### Andrew Larimer, Deepak Nagaraj, Daniel Olmstead, Michael Winton (W207-4-Summer 2018 Final Project)

# In[ ]:


# import necessary libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import util
from util import our_train_test_split

# set default options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 200)

get_ipython().magic('matplotlib inline')


# ## Load data and split class labels into separate array
# 
# Our utility function reads the merged dataset, imputes the column mean for missing numeric values, and then performs a stratified train-test split.

# In[ ]:


# read the "production" version of the cleaned & merged dataset
train_data_orig, test_data_orig, train_labels, test_labels = util.read_data(do_imputation=True)
print(train_data_orig.shape)
print(train_labels.shape)


# Filter to the columns that we will use in the model.  `district` and `zip`, while numeric, do not hold mathematical meaning and reduce accuracy and interpretability (it makes no sense to say that the higher or lower your district, the more or less likely you are to be a high-registering school).  `school_income_estimate` is too sparse to be be useful.  These columns are dropped from the model.

# In[ ]:


features_to_keep = [
                    #'district', 
                    #'zip',
                    'community_school', 
                    'economic_need_index', 
                    #'school_income_estimate',
                    'grade_7_enrollment',
                    'percent_ell', 
                    'percent_asian', 
                    'percent_black', 
                    'percent_hispanic',
                    'percent_black__hispanic', 
                    'percent_white', 
                    'student_attendance_rate',
                    'percent_of_students_chronically_absent',
                    'rigorous_instruction_percent', 
                    'rigorous_instruction_rating',
                    'collaborative_teachers_percent', 
                    'collaborative_teachers_rating',
                    'supportive_environment_percent', 
                    'supportive_environment_rating',
                    'effective_school_leadership_percent',
                    'effective_school_leadership_rating',
                    'strong_family_community_ties_percent',
                    'strong_family_community_ties_rating', 
                    'trust_percent', 
                    'trust_rating',
                    'student_achievement_rating', 
                    'average_ela_proficiency',
                    'average_math_proficiency', 
                    'grade_7_ela_all_students_tested',
                    'grade_7_ela_4s_all_students',
                    'grade_7_ela_4s_american_indian_or_alaska_native',
                    'grade_7_ela_4s_black_or_african_american',
                    'grade_7_ela_4s_hispanic_or_latino',
                    'grade_7_ela_4s_asian_or_pacific_islander', 
                    'grade_7_ela_4s_white',
                    'grade_7_ela_4s_multiracial',
                    'grade_7_ela_4s_limited_english_proficient',
                    'grade_7_ela_4s_economically_disadvantaged',
                    'grade_7_math_all_students_tested', 
                    'grade_7_math_4s_all_students',
                    'grade_7_math_4s_american_indian_or_alaska_native',
                    'grade_7_math_4s_black_or_african_american',
                    'grade_7_math_4s_hispanic_or_latino',
                    'grade_7_math_4s_asian_or_pacific_islander', 
                    'grade_7_math_4s_white',
                    'grade_7_math_4s_multiracial',
                    'grade_7_math_4s_limited_english_proficient',
                    'grade_7_math_4s_economically_disadvantaged',
                    'sie_provided',
                    'in_bronx',
                    'in_brooklyn',
                    'in_manhattan',
                    'in_queens',
                    'in_staten',
                    'number_of_students_english', 
                    'number_of_students_math',
                    'number_of_students_science', 
                    'number_of_students_social_studies',
                    'number_of_classes_english', 
                    'number_of_classes_math',
                    'number_of_classes_science', 
                    'number_of_classes_social_studies',
                    'average_class_size_english', 
                    'average_class_size_math',
                    'average_class_size_science',
                    'average_class_size_social_studies',
                    'school_pupil_teacher_ratio',
                    'gifted',
                    'selective'
                   ]

train_data = train_data_orig[features_to_keep]
test_data = test_data_orig[features_to_keep]
train_data.head()


# ## Hyperparameter Tuning
# Find the optimal C-score and penalty using GridSearchCV.

# In[ ]:


from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression

scaler = StandardScaler()
train_data_scaled = scaler.fit_transform(train_data)

lr = LogisticRegression(random_state=207)
penalty = ['l1', 'l2']
C = [0.01, 0.05, 0.1000, 0.2000, 0.3000, 0.4000, 0.5000, 1.000, 2.000, 3.000, 4.000]
hyperparameters = dict(C=C, penalty=penalty)
clf = GridSearchCV(lr, hyperparameters, cv=5, verbose=0)
best_model = clf.fit(train_data_scaled, train_labels)
best_penalty = best_model.best_estimator_.get_params()['penalty']
best_c = best_model.best_estimator_.get_params()['C']
print('Best Penalty:', best_penalty)
print('Best C:', best_c)


# ## Make Pipeline and K-fold validation
# Using five k-folds and the optimal hyperparameters from above, determine the overall accuracy and F1 score for the model.

# In[ ]:


from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.pipeline import make_pipeline

pipe = make_pipeline(StandardScaler(), LogisticRegression(C=best_c, penalty=best_penalty, random_state=207))
k_folds = 5
cv_scores = cross_validate(pipe, train_data, train_labels, cv=k_folds, scoring=['accuracy','f1'])
cv_f1 = cv_scores['test_f1'].mean()
util.print_cv_results(cv_scores)


# ## Apply model to the test set
# Check for overfitting by applying the model to the test set and reporting back accuracy and F1 score.

# In[ ]:


import sklearn.metrics as metrics

lr = LogisticRegression(C=best_c, penalty=best_penalty, random_state=207)
train_data_scaled, test_data_scaled = scaler.fit_transform(train_data), scaler.fit_transform(test_data)
lr.fit(train_data_scaled, train_labels)
predicted_labels = lr.predict(test_data_scaled)
lr_score_accuracy = metrics.accuracy_score(test_labels, predicted_labels)
lr_score_f1 = metrics.f1_score(test_labels, predicted_labels)

print("On the test set, the model has an accuracy of {:.2f}% and an F1 score of {:.2f}."
     .format(lr_score_accuracy*100, lr_score_f1))


# ## Examine coefficients
# For a better understanding of the model, including which factors are most important for predicting a high-registering school, we turn to an analysis of the model coefficients.  As the goal here is not prediction but comprehension, the first step is to recombine the data into a set that contains 100% of the schools.

# In[ ]:


# recombine train and test data into an aggregate dataset
X_orig = pd.concat([train_data_orig, test_data_orig])
X_i = pd.concat([train_data, test_data])
y = np.concatenate((train_labels,test_labels))
X_pos = X_i[y==1]
X_neg = X_i[y==0]
X_pos


# In[ ]:


from sklearn.model_selection import RepeatedStratifiedKFold

# Run coefficient analysis on 100% of the data
np_train_data = np.array(scaler.fit_transform(X_i))
np_train_labels = y

# Run k-fold cross-validation with 5 folds 10 times, which means every school is predicted 10 times.
folds = 5
repeats = 10
rskf = RepeatedStratifiedKFold(n_splits=folds, n_repeats= repeats, random_state=207)
fold_list = []

# Build multiple dataframes from the results, with columns for each k-fold
for f in range(1, (folds*repeats)+1):
    fold_list.append('k{}'.format(f))
# This contains the coefficients for every feature in every test
coefs = pd.DataFrame(index=train_data.columns, columns=fold_list)
# This contains the predicted value for each school tested (20% of the dataset each time)
predictions = pd.DataFrame(index=X_i.index, columns = fold_list)
# This contains the probabilities that each tested school will be a 0 or a 1, for use in later analysis
probs_0 = pd.DataFrame(index=X_i.index, columns = fold_list)
probs_1 = pd.DataFrame(index=X_i.index, columns = fold_list)

# Iterate through the Repeated Stratified K Fold, and and fill out the DataFrames
counter = 1
for train, test in rskf.split(np_train_data, np_train_labels):
    log = LogisticRegression(C=best_c, penalty=best_penalty, random_state=207)
    log.fit(np_train_data[train], np_train_labels[train])
    predicted_labels = log.predict(np_train_data[test])
    predicted_probs = log.predict_proba(np_train_data[test])
    coefs['k{}'.format(counter)] = log.coef_[0]
    predictions.iloc[test, counter-1] = predicted_labels
    probs_0.iloc[test, counter-1] = predicted_probs[:,0]
    probs_1.iloc[test, counter-1] = predicted_probs[:,1]
    counter += 1

# Find the average coefficient across all 50 regressions, and sort descending
coefs['avg'] = coefs.mean(axis=1)
sorted_coefs = coefs.sort_values(by='avg', ascending=False)
sorted_coefs


# ## Distributions
# ### Most positively-influential features
# Using the average coefficients, we can discover the features that have the greatest effect in predicting both a 1 (positive) or a zero (negative).  Histograms can show us the different distributions for high-registering and low-registering schools in these categories.

# In[ ]:


# Get the top and bottom 5 most influential coefficients
top_features, bottom_features = list(sorted_coefs.index[:6]), list(sorted_coefs.index[-6:])
fig = plt.figure(figsize=(20,60))
for c in top_features:
    ax = fig.add_subplot(6,2,top_features.index(c)+1)
    ax.set_title('Distribution for {}'.format(c), fontsize=17)
    ax.hist(X_pos[c], bins=20, alpha=0.5, label="high registrants", density=True)
    ax.hist(X_neg[c], bins=20, alpha=0.5, label="low registrants", density=True)
    ax.legend()
plt.show()


# ### Most negatively-influential features

# In[ ]:


fig = plt.figure(figsize=(20,60))
for c in bottom_features:
    ax = fig.add_subplot(6,2,bottom_features.index(c)+1)
    ax.set_title('Distribution for {}'.format(c), fontsize=17)
    ax.hist(X_pos[c], bins=20, alpha=0.5, label="high registrants", density=True)
    ax.hist(X_neg[c], bins=20, alpha=0.5, label="low registrants", density=True)
    ax.legend()
plt.show()


# ## Examining Wrong Answers
# 

# In[ ]:


import seaborn as sns
fig, ax = plt.subplots(figsize=(10,10))

ax = sns.regplot(X_pos.grade_7_math_4s_hispanic_or_latino, X_pos.grade_7_ela_4s_hispanic_or_latino, label="High Registrations")
ax = sns.regplot(X_neg.grade_7_math_4s_hispanic_or_latino, X_neg.grade_7_ela_4s_hispanic_or_latino, label="Low Registrations")
ax.legend()


# In[ ]:


fig, ax = plt.subplots(figsize=(10,10))
ax = sns.regplot(X_i.grade_7_math_4s_hispanic_or_latino, y, logistic=True, label="Math")
ax = sns.regplot(X_i.grade_7_ela_4s_hispanic_or_latino, y, logistic=True, label="English")
ax.set_xlabel('Number of Students achieving a score of 4', fontsize=15)
ax.legend()


# In[ ]:


fig, ax = plt.subplots(figsize=(10,10))
ax = sns.regplot(X_i.percent_asian, y, logistic=True, label="% Asian")
ax = sns.regplot(X_i.percent_hispanic, y, logistic=True, label="% Hispanic")
ax.set_xlabel('Percent of school either Asian or Hispanic', fontsize=15)

ax.legend()


# In[ ]:


fig, ax = plt.subplots(figsize=(10,10))
ax = sns.regplot(X_i.economic_need_index, y, logistic=True, label="Economic Need Index")
ax.set_xlabel('Economic Need Index', fontsize=15)


# In[ ]:


fig, ax = plt.subplots(figsize=(10,10))
ax.set_title('Distribution for {}'.format('Economic Need Index'), fontsize=17)
ax.hist(X_pos['economic_need_index'], bins=20, alpha=0.5, label="high registrants", density=True)
ax.hist(X_neg['economic_need_index'], bins=20, alpha=0.5, label="low registrants", density=True)
ax.legend()


# ### Heatmap Analysis
# We can build a table of all the kfold predictions, and see the degree to which the model got each school right or wrong

# In[ ]:


predictions['1s'] = predictions.iloc[:,:50].sum(axis=1)
predictions['0s'] = (predictions.iloc[:,:50]==0).sum(axis=1)
predictions['true'] = y

predictions['1_prob'] = probs_1.mean(axis=1)
predictions['0_prob'] = probs_0.mean(axis=1)
predictions = predictions.sort_values(by=['1_prob'], ascending=False)


# In[ ]:


# Create a table of raw results, along with the number of votes each received and the true value
X_predicted = pd.concat([X_i, predictions['1s'], predictions['0s'], predictions['true'], predictions['1_prob']], axis=1, join_axes=[X_i.index])
# Rename the y columns to be more descriptive
X_predicted.rename(columns={0:"high_registrations"}, inplace=True)
# Sort by number of votes, most votes for 1 at the top and most votes for 0 at the bottom
X_predicted = X_predicted.sort_values(by=['1_prob'], ascending=False)

# Normalize the values of the data columns
scaled_X_predicted = scaler.fit_transform(X_predicted)
# Multiply the normalized value by the average coefficient to get a weighted influence score
avg_coefs = np.array(coefs['avg'])
weighted_values = np.multiply(scaled_X_predicted[:, :-4], avg_coefs)
# Make a new copy of the results dataframe, and paste in the scaled values for the data columns
X_result_weighted = X_predicted.copy()
X_result_weighted.iloc[:, :-4] = weighted_values
# Manually scale the vote columns to between -1.5 and 1.5 so they don't overweight the heatmap
X_result_weighted.iloc[:, -4:-3] = predictions['1_prob']
X_result_weighted.iloc[:, -3:-2] = predictions['0_prob']
X_result_weighted = X_result_weighted.sort_values(by=['1s', '0s'], ascending=[False, True])
#X_predicted = X_predicted.set_index(X_result_weighted.index)

#X_result_weighted.iloc[:, -3:-1] = np.multiply(X_predicted.iloc[:,-3:-1], .15)

# Check the variation in every column, and drop the columns that don't show much effect on the result
drop_cols = ['1_prob']
for c in X_result_weighted.columns:
    if X_result_weighted[c].max() - X_result_weighted[c].min() < .6:
        drop_cols.append(c)
X_result_weighted_trimmed = X_result_weighted.drop(drop_cols, axis=1)
X_result_weighted_trimmed.head()


# In[ ]:


fig, ax = plt.subplots(figsize=(18,200))
fig.patch.set_facecolor('white')
im = ax.imshow(X_result_weighted_trimmed, cmap='viridis')
ax.xaxis.tick_top()
ax.set_xticks(np.arange(len(X_result_weighted_trimmed.columns)))
ax.set_yticks(np.arange(len(X_result_weighted_trimmed.index)))
ax.set_xticklabels(X_result_weighted_trimmed.columns)
labels = X_orig.loc[:,'school_name'].reindex([X_result_weighted_trimmed.index])
ax.set_yticklabels(labels)
plt.setp(ax.get_xticklabels(), rotation=90, ha="left", va="center", rotation_mode="anchor")

for i in range(len(X_result_weighted_trimmed.index)):
    for j in range(len(X_result_weighted_trimmed.columns[1:])+1):
        text = ax.text(j, i, "{:n}".format(round(X_predicted.loc[X_result_weighted_trimmed.index[i], X_result_weighted_trimmed.columns[j]], 0)),
                       ha="center", va="center", color="w")
plt.show()


# It is perhaps most useful to examine the false positives - that is, schools that did NOT have high SHSAT registrations, but that the model thought SHOULD have.  We'll put the threshhold at 5 or more incorrect "true" classifications, and rank them in descending order (ie, the schools the model got most consistently wrong at the top).

# In[ ]:


false_positives = predictions[predictions['true']==0]
false_positives = false_positives[false_positives['1s'] > 5]['1s']

fp_result = pd.concat([false_positives, X_i], axis=1, join='inner')
fp_result.head()


# In[ ]:


scaled_fp_X = scaler.fit_transform(fp_result.iloc[:,1:])
avg_coefs = np.array(coefs['avg'])
weighted_values = np.multiply(scaled_fp_X, avg_coefs)
fp_result_weighted = fp_result.copy()
fp_result_weighted.iloc[:, 1:] = weighted_values
# Drop the columns that don't have any evidence of influential values
drop_cols = []
for c in fp_result_weighted.columns:
    if fp_result_weighted[c].max() - fp_result_weighted[c].min() < .5:
        drop_cols.append(c)
fp_result_weighted_trimmed = fp_result_weighted.drop(drop_cols, axis=1)
fp_result_weighted_trimmed.head()


# In[ ]:


fig, ax = plt.subplots(figsize=(18,20))
im = ax.imshow(fp_result_weighted_trimmed.iloc[:,1:], cmap='viridis')
ax.xaxis.tick_top()
ax.set_xticks(np.arange(len(fp_result_weighted_trimmed.columns[1:])))
ax.set_yticks(np.arange(len(fp_result_weighted_trimmed.index)))
ax.set_xticklabels(fp_result_weighted_trimmed.columns[1:])
labels = X_orig.loc[:,'school_name'].reindex([fp_result_weighted_trimmed.index])
ax.set_yticklabels(labels)
#ax.set_yticklabels(fp_result_weighted_trimmed.index)
plt.setp(ax.get_xticklabels(), rotation=90, ha="left", va="center", rotation_mode="anchor")

for i in range(len(fp_result_weighted_trimmed.index)):
    for j in range(len(fp_result_weighted_trimmed.columns[1:])):
        text = ax.text(j, i, round(fp_result.loc[fp_result_weighted_trimmed.index[i], fp_result_weighted_trimmed.columns[j+1]], 1),
                       ha="center", va="center", color="w")
plt.show()


# In[ ]:


false_negatives = predictions[predictions['true']==1]
false_negatives = false_negatives[false_negatives['0s'] > 5]['0s']

fn_result = pd.concat([false_negatives, X_i], axis=1, join='inner')
fn_result.head()


# In[ ]:


scaled_fn_X = scaler.fit_transform(fn_result.iloc[:,1:])
weighted_values = np.multiply(scaled_fn_X, avg_coefs)
fn_result_weighted = fn_result.copy()
fn_result_weighted.iloc[:, 1:] = weighted_values
# Drop the columns that don't have any evidence of influential values
drop_cols = []
for c in fn_result_weighted.columns:
    if fn_result_weighted[c].max() - fn_result_weighted[c].min() < .5:
        drop_cols.append(c)
fn_result_weighted_trimmed = fn_result_weighted.drop(drop_cols, axis=1)
fn_result_weighted_trimmed.head()


# In[ ]:


fig, ax = plt.subplots(figsize=(18,20))
im = ax.imshow(fn_result_weighted_trimmed.iloc[:,1:], cmap='viridis')
ax.xaxis.tick_top()
ax.set_xticks(np.arange(len(fn_result_weighted_trimmed.columns[1:])))
ax.set_yticks(np.arange(len(fn_result_weighted_trimmed.index)))
ax.set_xticklabels(fn_result_weighted_trimmed.columns[1:])
labels = X_orig.loc[:,'school_name'].reindex([fn_result_weighted_trimmed.index])
ax.set_yticklabels(labels)
#ax.set_yticklabels(fn_result_weighted_trimmed.index)
plt.setp(ax.get_xticklabels(), rotation=90, ha="left", va="center", rotation_mode="anchor")

for i in range(len(fn_result_weighted_trimmed.index)):
    for j in range(len(fn_result_weighted_trimmed.columns[1:])):
        text = ax.text(j, i, round(fn_result.loc[fn_result_weighted_trimmed.index[i], fn_result_weighted_trimmed.columns[j+1]], 1),
                       ha="center", va="center", color="w")
plt.show()


# ## Final ranking for PASSNYC

# In[ ]:


# Just the columns of interest
final_features = ['dbn',
              'school_name',
              'grade_7_enrollment',
              'num_shsat_test_takers']
# Convert the percent columns to proper floats
pct_features = ['pct_test_takers',
               'percent_black__hispanic']
df_pct = np.multiply(X_orig[pct_features], .01)

# Merge these columns to one DataFrame, along with number of 1 predictions and the true value
df_final = pd.concat([X_orig[final_features], df_pct, predictions['1s'], predictions['true']], axis=1)

# Determine the number of test takers this school would have needed to meet the median percentage of high_registrations
median_pct = np.median(X_orig[y==1]['pct_test_takers'])/100
predicted_test_takers = np.multiply(df_final['grade_7_enrollment'], median_pct)

# Subtract the number of actual test takers from the hypothetical median number
delta = predicted_test_takers - df_final['num_shsat_test_takers']

# Multiply the delta by the minority percentage of the school to estimate how many minority students did not take the test
df_final['minority_delta'] = np.round(np.multiply(delta, df_final['percent_black__hispanic']), 0)

# Multiply the minority delta by the percentage of 1 votes to get a confidence-adjusted 'score', and sort by this.
df_final['score'] = np.multiply(df_final['minority_delta'], df_final['1s']/10)
df_final = df_final.sort_values(by='score', ascending=False)

# Create a rank order column
df_final.insert(0, 'rank', range(1,df_final.shape[0]+1))

# Write to CSV
df_final.to_csv('results/results.logreg.csv')
df_final

