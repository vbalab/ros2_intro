import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleMoveNode(Node):
    def __init__(self):
        super().__init__('turtle_mover')

        self.pub = self.create_publisher(
            msg_type=Twist,
            topic='/turtle1/cmd_vel',
            qos_profile=1,
        )

        self.timer = self.create_timer(0.1, self.move)

    def move(self):
        self.msg = Twist()
        self.msg.linear.x = 2.0
        self.msg.angular.z = 1.0

        self.pub.publish(self.msg)


def main():
    rclpy.init()
    node = TurtleMoveNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
