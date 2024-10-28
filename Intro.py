import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import cv2
import numpy as np

st.set_page_config(page_title="Intro",page_icon="👋")

st.write("# Need to turn a crappy pdf into markdown text? 👋")

st.markdown('''
# Deskewing and Extracting Text from Crappy Scans
I recently had a need to extract the text from some pdf's. The content of thd PDF's were 
basically black and white photographs of a typewritten document. The photographs themselves
weren't straight at all.I figured it might be a fun project to attemp to have an app that could deskew the pdf's for me to allow the text to be extracted.

I present two different methods of deskewing a pdf here


**EAST (Efficient accurate scene text detector) and Hough Lines**

As the name suggests, it’s a very robust(accurate) scene text detector.

![](https://miro.medium.com/v2/resize:fit:1166/0*nfN1SdCEvbRfGyov)

It's a Fully Convolutional Network (FCN) which outputs per-pixel predictions of words or text lines. It also uses Non-Maximum Suppression (NMS) on the geometric map as a post-processing step.

The geometric map will be one of RBOX(4 channels for bbx coordinates, 1 channel for text rotation angle) or QUAD(8 channels to denote the coordinate shift from four corner vertices).

It uses a weighted sum of losses for the score map and the geometry as the loss function.

![](https://miro.medium.com/v2/resize:fit:508/0*3y5--Z05oaGgkL1k)

Hough transform is a feature extraction technique. The Hough Line Transform is used to detect straight lines. To apply the Transform, a preprocessing is done for edge detection The Hough line method also provides the angle, made by the line with the origin as shown.
![](https://miro.medium.com/v2/resize:fit:1400/0*tRJoBja3H8_PUHIT)

![](https://miro.medium.com/v2/resize:fit:1400/0*Vg7k0hjSo97JtCQI)
The lines seem to cross all over the image but we only need to filter in the potentially horizontal lines to calculate the angle. To achieve that, we will take the most commonly occurring angle after filtering and will rotate the image.

** OpenCV Minimum Area Rectangle **

The below image shows 2 rectangles, the green one is the normal bounding rectangle while the red one is the minimum area rectangle. See how the red rectangle is rotated.  

![](https://i0.wp.com/theailearner.com/wp-content/uploads/2020/11/min_area_rect.jpg?resize=279%2C278&ssl=1)

**Source:  [OpenCV](https://docs.opencv.org/master/dd/d49/tutorial_py_contour_features.html)**

OpenCV provides a function cv2.minAreaRect() for finding the minimum area rotated rectangle. This takes as input a 2D point set and returns a Box2D structure which contains the following details – (center(x, y), (width, height), angle of rotation). The syntax is given below.

    (center(x,  y),  (width,  height),  angle of rotation)  =  cv2.minAreaRect(points)

But to draw a rectangle, we need 4 corners of the rectangle. So, to convert the Box2D structure to 4 corner points, OpenCV provides another function cv2.boxPoints(). This takes as input the Box2D structure and returns the 4 corner points. The 4 corner points are ordered clockwise starting from the point with the highest y. The syntax is given below.

    points  =  cv2.boxPoints(box)

Before drawing the rectangle, you need to convert the 4 corners to the integer type. You can use np.int32 or np.int64 (Don’t use np.int8 as it permits value up to 127 and leads to truncation after that). Sometimes, you might see np.int0 used, don’t get confused, this is equivalent to np.int32 or np.int64 depending upon your system architecture. The full code is given below.

    rect  =  cv2.minAreaRect(cnt)
    box  =  cv2.boxPoints(rect)
    box  =  np.int0(box)

Once the 4 coordinates are obtained, you can easily draw the rectangle. Now, let’s discuss about the angle of rotation.

### Angle of Rotation

As we already discussed that the 4 corner points are ordered clockwise starting from the point with the highest y as shown below. If 2 points have the same highest y, then the rightmost point is the starting point. The points are numbered as 0,1,2,3 (0-starting, 3-end).

![](https://i0.wp.com/theailearner.com/wp-content/uploads/2020/11/minre.jpg?resize=592%2C311&ssl=1)

So, the angle of rotation given by OpenCV’s cv2.minAreaRect() is actually the angle between the line (joining the starting and endpoint) and the horizontal as shown below.

![](https://i0.wp.com/theailearner.com/wp-content/uploads/2020/11/minre1.jpg?resize=625%2C317&ssl=1)

**Thus the angle value always lies between [-90,0)**. Why? because if the object is rotated more than 90 degrees, then the next edge is used to calculate the angle from the horizontal. And thus the calculated angle always lies between [-90,0). See the below image where the green line shows the line joining the starting and endpoint that is used to calculate the angle. Also, see how the starting and endpoint change when the object is rotated. The points are numbered as 0,1,2,3 (0-starting, 3-end).
''')