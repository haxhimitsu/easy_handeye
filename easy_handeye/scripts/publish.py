#!/usr/bin/env python3

import rospy
import tf2_ros
import geometry_msgs.msg
from easy_handeye.handeye_calibration import HandeyeCalibration


rospy.init_node('handeye_calibration_publisher')
while rospy.get_time() == 0.0:
    pass

inverse = rospy.get_param('inverse')
filename = rospy.get_param('calibration_file')

if filename == '':
    rospy.logdebug('No path specified for the calibration file, loading from the standard location')
    filename = HandeyeCalibration.filename_for_namespace(rospy.get_namespace())

rospy.loginfo("Loading the calibration from file: %s", filename)
calib = HandeyeCalibration.from_filename(filename)

if calib.parameters.eye_on_hand:
    overriding_robot_effector_frame = rospy.get_param('robot_effector_frame')
    if overriding_robot_effector_frame != "":
        calib.transformation.header.frame_id = overriding_robot_effector_frame
else:
    overriding_robot_base_frame = rospy.get_param('robot_base_frame')
    if overriding_robot_base_frame != "":
        calib.transformation.header.frame_id = overriding_robot_base_frame
overriding_tracking_base_frame = rospy.get_param('tracking_base_frame')
if overriding_tracking_base_frame != "":
    calib.transformation.child_frame_id = overriding_tracking_base_frame

rospy.loginfo('loading calibration parameters into namespace {}'.format(
    rospy.get_namespace()))
HandeyeCalibration.store_to_parameter_server(calib)
r = rospy.Rate(1000) # 10hz
while not rospy.is_shutdown():
    orig = calib.transformation.header.frame_id  # tool or base link
    dest = calib.transformation.child_frame_id  # tracking_base_frame

    broadcaster = tf2_ros.StaticTransformBroadcaster()
    static_transformStamped = geometry_msgs.msg.TransformStamped()

    static_transformStamped.header.stamp = rospy.Time.now()
    static_transformStamped.header.frame_id = orig
    static_transformStamped.child_frame_id = dest

    static_transformStamped.transform = calib.transformation.transform

    broadcaster.sendTransform(static_transformStamped)
    # rospy.spin()
    r.sleep()