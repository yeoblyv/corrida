"""
Find the next place to explore and show it in Foxglove.

For every new map from slam_toolbox the node publishes the frontiers and the nearest one
as the goal. It doesn't drive the robot yet.
"""

import rclpy
from geometry_msgs.msg import Point, PoseStamped
from nav_msgs.msg import OccupancyGrid
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker

from corrida_exploration import frontiers

ROBOT_FRAME = "base_link"
# m, an opening has to be wider than the robot (about 0.35 m) to count
MIN_FRONTIER_SIZE = 0.4
# m, how far from the robot the search may start if its cell isn't free
START_REACH = 0.15


class Explorer(Node):
    def __init__(self) -> None:
        super().__init__("explorer")
        # same QoS as slam_toolbox's map (transient local), so its last map comes right away
        map_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        # "/map" with the slash, slam_toolbox publishes it outside the robot namespace
        self.create_subscription(OccupancyGrid, "/map", self.on_map, map_qos)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.frontier_pub = self.create_publisher(Marker, "frontiers", 1)
        self.goal_pub = self.create_publisher(PoseStamped, "exploration_goal", 1)

    def on_map(self, map_msg: OccupancyGrid) -> None:
        """Look for frontiers in a new map and publish the nearest one as the goal."""
        try:
            # Time() asks for the newest transform there is
            robot = self.tf_buffer.lookup_transform(map_msg.header.frame_id, ROBOT_FRAME, Time())
        except TransformException as error:
            self.get_logger().warn(f"no robot pose from tf yet: {error}")
            return

        info = map_msg.info
        # slam_toolbox doesn't rotate the map origin, so x and y are enough
        origin = (info.origin.position.x, info.origin.position.y)
        grid = frontiers.to_rows(list(map_msg.data), info.width)
        position = (robot.transform.translation.x, robot.transform.translation.y)
        robot_cell = frontiers.world_to_cell(position, origin, info.resolution)
        start = frontiers.nearest_free_cell(grid, robot_cell, round(START_REACH / info.resolution))
        if start is None:
            self.get_logger().warn("robot is not on a free part of the map")
            return

        steps = frontiers.reachable_cells(grid, start)
        found = frontiers.find_frontiers(grid, steps, round(MIN_FRONTIER_SIZE / info.resolution))
        self.publish_frontiers(found, map_msg)
        goal_cell = frontiers.nearest_goal(found, steps)
        if goal_cell is None:
            self.get_logger().info("no frontiers left to explore")
            return

        goal = PoseStamped()
        goal.header = map_msg.header
        x, y = frontiers.cell_to_world(goal_cell, origin, info.resolution)
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.orientation.w = 1.0
        self.goal_pub.publish(goal)
        distance = steps[goal_cell] * info.resolution
        self.get_logger().info(
            f"{len(found)} frontiers, nearest at ({x:.2f}, {y:.2f}), {distance:.1f} m to drive"
        )

    def publish_frontiers(self, found: list[list[frontiers.Cell]], map_msg: OccupancyGrid) -> None:
        """Publish the frontier cells as small squares for Foxglove's 3D panel."""
        info = map_msg.info
        origin = (info.origin.position.x, info.origin.position.y)
        marker = Marker()
        marker.header = map_msg.header
        marker.ns = "frontiers"
        marker.type = Marker.CUBE_LIST
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = info.resolution
        marker.scale.y = info.resolution
        marker.scale.z = 0.01
        marker.color.b = 1.0
        marker.color.a = 1.0
        for cells in found:
            for cell in cells:
                x, y = frontiers.cell_to_world(cell, origin, info.resolution)
                marker.points.append(Point(x=x, y=y))
        self.frontier_pub.publish(marker)


def main() -> None:
    rclpy.init()
    node = Explorer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
