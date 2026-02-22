import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from geometry_msgs.msg import Twist


class TurtleMoveNode(Node):
    def __init__(self):
        super().__init__('turtle_move_server')

        self.pub = self.create_publisher(
            msg_type=Twist,
            topic='/turtle1/cmd_vel',
            qos_profile=1,
        )

        self.srv = self.create_service(
            srv_type=Trigger,
            srv_name='/move_once',
            callback=self.move,
        )

    def move(self, request, response):
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 1.0

        while True:
            self.pub.publish(msg)


def main():
    rclpy.init()
    node = TurtleMoveNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
