import re

text = """
Skip to main content
University Header Menu
MyU
One Stop
Search
Statistics
Unit Menu
Undergraduate
Graduate
People
Research & Engagement
Alumni & Friends
News & Events
About
In This Section
Faculty
Staff
Graduate Students
Advisory Board
Faculty
The School of Statistics has an internationally distinguished faculty, including many elected fellows of the major statistical organizations such as the American Statistical Association, the Institute of Mathematical Statistics, and the International Statistical Institute. Also, many of our faculty members are or have been editors or associate editors of major journals. Additionally, several have been nominated for, or are the recipients of, awards for excellence in teaching.

Name	Contact	Specialty
Sara Algeri            
Associate Professor 
Director of Undergraduate Studies	362 Ford Hall
612-625-4005 
salgeri@umn.edu	Statistical inference, computational statistics, astrostatistics
Jie Ding
Associate Professor	366 Ford Hall
dingj@umn.edu	Time series, model selection, inference methodology, applications in audio/video processing, finance
Charles Doss
Associate Professor	389 Ford Hall
612-625-5819
cdoss@umn.edu	Nonparametric estimation and inference
Charles Geyer
Professor	356 Ford Hall
612-625-8511
geyer@umn.edu	Constrained maximum likelihood, Markov chain Monte Carlo, Monte Carlo likelihood, spatial statistics
Birgit Grund
Professor	381 Ford Hall
612-624-8076
birgit@umn.edu	Design and analysis of clinical trials, research in HIV/AIDS, Ebola, and COVID-19
Nathaniel Helwig
Associate Professor	383 Ford Hall
612-625-7515
helwig@umn.edu	Computational statistics, smoothing splines, multimode/tensor analysis, nonparametric methods, neuroimaging, psychometrics
Galin Jones
Professor
Director of the School of Statistics	313A Ford Hall
galin@umn.edu	Markov chain Monte Carlo methodology, decison theory, biological and environmental applications
Tianxi Li
Assistant Professor	376 Ford Hall
tianxili@umn.edu	Statistical network analysis, statistical machine learning
Xiaoou Li
Associate Professor	347 Ford Hall
612-625-1816
lixx1766@umn.edu	Sequential analysis and adaptive design, latent variable models, graphical models, psychometrics
Aaron Molstad
Assistant Professor	384 Ford Hall
amolstad@umn.edu	Statistical genetics and genomics, multivariate analysis, numerical optimization
Qian Qin
Assistant Professor	357 Ford Hall
qqin@umn.edu	Markov chain Monte Carlo, convergence rates of Markov chains
Adam Rothman
Professor
Director of Graduate Studies	367 Ford Hall
612-626-0346 
arothman@umn.edu	Multivariate analysis and statistical computing in
high dimensions
Xiaotong Shen
Professor	384 Ford Hall
612-624-7098
xshen@umn.edu	Machine learning and data science, inference and prediction, statistical applications in engineering and health science
Lu Yang
Assistant Professor 
Director of the Lynn Y. S. Lin Consulting Center	385 Ford Hall
luyang@umn.edu	Multivariate analysis, regression model diagnostics, nonparametric methods, insurance analytics
Hui Zou
Professor	312 Ford Hall
612-625-8355
zouxx019@umn.edu	Statistical methodology and theory
Associate Faculty
Name	Contact	 
Kazeem Adepoju
Senior Lecturer	465 Ford Hall
612-625-2858
kadepoju@umn.edu 	 
Georgia (Zhuozhi) Huang
Teaching Specialist	
453 Ford Hall
612-625-8730
zz-huang@umn.edu
 
Barbara Kuzmak
Senior Lecturer	485 Ford Hall
612-625-4897
bkuzmak@umn.edu	 
Eugenie Ngandjeu Nya
Teaching Specialist	475 Ford Hall
ennya@umn.edu 	 
Yuyoung Park
Teaching Specialist	487 Ford Hall
612-625-4897
parky@umn.edu	 
Affiliate Faculty 
Name	Contact	 
Xuan Bi
Associate Professor	3-233 Carlson School of Management
612-626-7813
xbi@umn.edu	 


Postdocs
Name	Contact
Qiuyun Zhu 
IRSA Faragher Distinguished Postdoctoral Fellow	368 Ford Hall
qzhu@umn.edu                                           
Visiting Faculty and Scholars
Name	Contact
Xin-Yu Tian              	467 Ford Hall
tianx@umn.edu
Emeriti
Name                                  	Contact
Yuhong Yang
Professor Emeritus	yangx374@umn.edu
Tiefeng Jiang
Professor Emeritus	jiang040@umn.edu
Christopher Bingham
Professor Emeritus	kb@umn.edu
R. Dennis Cook
Professor Emeritus	484 Ford Hall
rdcook@umn.edu
Morris L. Eaton
Professor Emeritus	eaton@stat.umn.edu
Douglas M. Hawkins
Professor Emeritus	dhawkins@umn.edu
Glen Meeden
Professor Emeritus	392 Ford Hall
gmeeden@umn.edu
Gary W. Oehlert
Professor Emeritus	320 Ford Hall
612-625-1557
gary@umn.edu
William Sudderth
Professor Emeritus	392 Ford Hall
sudde001@umn.edu
Sanford Weisberg
Professor Emeritus	sandy@umn.edu
College of Liberal Arts' wordmark
School of Statistics
313 Ford Hall
224 Church St SE
Minneapolis, MN 55455

Connect
info@stat.umn.edu
612-625-8046
 
 
 
Make a Gift
Find information on ways to give to the School of Statistics
Give
© 2025 Regents of the University of Minnesota. All rights reserved. The University of Minnesota is an equal opportunity educator and employer. Privacy Statement
CLA is committed to making its digital resources accessible. Report Web Disability-Related Issue"""

email_addresses = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

for email in email_addresses:
    print(email)