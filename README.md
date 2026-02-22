# Annotated Steps

## Workflow

### 0) Launch docker container

```bash
docker run -p 6080:80 --shm-size=512m \
    -v "$PWD/src":/home/ubuntu/ws/src \
    tiryoh/ros2-desktop-vnc:jazzy
```

- Enter: `http://127.0.0.1:6080` in browser
- Connect to container in VSCode

All of the following bash commands need to be executed in container's terminal.

### 1) Create workspace + package

```bash
mkdir -p ~/ws/src
cd ~/ws/src

ros2 pkg create --build-type ament_python turtle_mover --dependencies rclpy geometry_msgs std_srvs
```

- creates standard package structure
- declares dependencies so runtime/build environment is correct

### 2) Write the node

Create mover node:

```bash
touch ~/ws/src/turtle_mover/turtle_mover/mover_server.py
```

And fill it with:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleMover(Node):
    def __init__(self):
        super().__init__('turtle_mover')

        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.timer = self.create_timer(0.1, self.on_timer)

        self.msg = Twist()
        self.msg.linear.x = 2.0
        self.msg.angular.z = 1.0

    def on_timer(self):
        self.pub.publish(self.msg)


def main():
    rclpy.init()
    node = TurtleMover()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 3) Register entry point

Edit: `~/ws/src/turtle_mover/setup.py` and ensure:

```python
entry_points={
    'console_scripts': [
        'move = turtle_mover.mover_server:main',
    ],
},
```

- creates a runnable command named `move`
- `ros2 run turtle_mover move` resolves to that `main()`

### 4) Build & Run

In one terminal:

```bash
ros2 run turtlesim turtlesim_node
```

In another terminal:

```bash
colcon build
source ~/ws/srt/install/setup.bash

ros2 run turtle_mover move
```

## For V4

In addition to all previous steps do

```bash
ros2 service call /move_once std_srvs/srv/Trigger {}

cd ~/ws/src
ros2 pkg create turtle_interfaces --build-type ament_cmake
mkdir -p ~ws/src/turtle_interfaces/srv
touch ~/ws/src/turtle_interfaces/srv/GoTo.srv
```

Edit `~/ws/src/turtle_interfaces/srv/GoTo.srv`:

```srv
float32 x
float32 y
---
bool success
string message
```

Edit `~/ws/src/turtle_interfaces/CMakeLists.txt`:

```cmake
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/GoTo.srv"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

Edit `~/ws/src/turtle_interfaces/package.xml`:

```xml
cmake_minimum_required(VERSION 3.8)
project(turtle_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/GoTo.srv"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

Then

- In 1st terminal:

    ```bash
    ros2 run turtlesim turtlesim_node
    ```

- In 2nd terminal:

    ```bash
    colcon build
    source ~/ws/srt/install/setup.bash

    ros2 run turtle_mover move
    ```

- In 3rd terminal:

    ```bash
    source ~/ws/srt/install/setup.bash
    ros2 service call /go_to turtle_interfaces/srv/GoTo "{x: 9.0, y: 9.0}"
    ```
