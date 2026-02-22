import math
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtle_interfaces.srv import GoTo  # type: ignore[attr-defined]
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup


@dataclass
class PoseXY:
    x: float
    y: float


def angle_diff(target: float, current: float) -> float:
    d = target - current
    return (d + math.pi) % (2 * math.pi) - math.pi


class TurtleMoveNode(Node):
    def __init__(self):
        super().__init__('turtle_move_server')

        turtle_name = "turtle1"

        self.sub_group = ReentrantCallbackGroup()
        self.srv_group = ReentrantCallbackGroup()

        self.sub = self.create_subscription(
            msg_type=Pose,
            topic=f'/{turtle_name}/pose',
            callback=self.on_pose,
            qos_profile=1,
            callback_group=self.sub_group,
        )

        self.pub = self.create_publisher(
            msg_type=Twist,
            topic=f'/{turtle_name}/cmd_vel',
            qos_profile=1,
        )

        self.srv = self.create_service(
            srv_type=GoTo,
            srv_name='/go_to',
            callback=self.move,
            callback_group=self.srv_group,
        )

    def _stop_moving(self) -> None:
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0

        self.pub.publish(msg)

    def _go_to_point(
        self,
        target_point: PoseXY,
        *,
        tol: float = 0.05,
    ) -> None:
        msg = Twist()

        while True:
            p = self.pose

            dx = target_point.x - p.x
            dy = target_point.y - p.y
            dist = math.hypot(dx, dy)

            if dist <= tol:
                self._stop_moving()
                return

            desired = math.atan2(dy, dx)

            msg.angular.z = 2 * angle_diff(desired, p.theta)
            msg.linear.x = dist

            self.pub.publish(msg)

    def on_pose(self, msg: Pose):
        print(f"on_pose: {msg}")
        self.pose = msg

    def move(self, request, response):
        self._go_to_point(PoseXY(request.x, request.y))

        response.success = True
        response.message = f"Reached ({request.x}, {request.y})."
        return response


def main():
    rclpy.init()
    node = TurtleMoveNode()
    
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
