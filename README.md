# Face Mask Detector with Alert Funtion
Infectious coronavirus disease (COVID-19) has become a public health hazard in China and around the world since the first occurrence in Wuhan. 
This pandemic is wreaking havoc on economies and societies all around the world. 
However, wearing a mask that prevents droplets from spreading in the air is still conducive to fighting this epidemic. 
Wearing protective masks has become a new normal. Thus, mask detection has become a key task in assisting the worldwide society. 
As a result, the goal of this study is to develop a real-time mask detection system that can identify the presence of the mask. 

OpenCV, TensorFlow, and Keras are some of the basic machine learning packages used in this research to achieve this goal. 
In this case, the MobileNetV2 model is applied. 

A dataset of 3830 images with the labels "with mask" and "without mask" was obtained and used to train the mask detection model. 
By using the mask detection model, people who were not wearing the masks were detected. 

To prove the practical applicability, the system's performance is measured in terms of accuracy, recall, precision, and F1-score. 
After implementing and deploying the model, the confidence score of the model is 99%. All evaluation metrics also reached 99%. 
Hence, the solution can track persons who are wearing or are not wearing masks in real time and send out notifications when violations occur on-site or in public places. 

This may be combined with current embedded camera infrastructure to do these analyses, which can be employed in a variety of verticals such as airport gates or office buildings. 
This system also can be exploited in wide applications such as, COVID-19 control, other epidemic control, and face mask detection. 
