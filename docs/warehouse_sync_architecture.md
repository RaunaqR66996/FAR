# Warehouse Digital Twin Sync Architecture

## Overview

This document outlines a three-tier system that fuses warehouse perception (LiDAR + video), maintains a 3D digital twin, and runs heuristic optimization for inventory allocation. The goal is to keep the digital twin in lockstep with real-world motion while enabling low-latency space and labor optimization.

## Three-Tier Architecture

1. **Edge Layer (Perception + Preprocessing)**
   - Collects LiDAR point clouds and camera frames in real time.
   - Performs downsampling (e.g., voxel grid filtering) and basic denoising to reduce bandwidth.
   - Synchronizes timestamps across devices using **PTP (IEEE 1588)**.
   - Ships sensor packets over **gRPC** with protobuf payloads.

2. **Digital Twin Layer (Source of Truth)**
   - Maintains the canonical 3D state (structures, zones, and inventory positions).
   - Converts fused sensor data into vectorized representations (AABB bounds + slot vectors).
   - Uses a layered scene graph (e.g., **OpenUSD** or **NVIDIA Omniverse**) to isolate static structure, dynamic inventory, and live observations.

3. **Optimization Layer (Brain)**
   - Receives updated space availability + order signals.
   - Executes heuristic placement (Best-Fit Decreasing or First-Fit Decreasing) with domain rules like fast-mover priority.
   - Writes allocation decisions back into the digital twin so the visualization and execution services stay consistent.

## Sensor Fusion Pipeline

### Synchronization

* **Temporal alignment** is mandatory before fusing LiDAR and video. A 50ms offset can introduce ghosting when projecting 2D pixels into 3D space.
* Use **PTP** and record timestamps on the sensor at acquisition time. Align on the server using bounded skew windows (e.g., ±15ms).

### Projection

1. **Calibrate** camera intrinsics and LiDAR-to-camera extrinsics.
2. **Project** pixel coordinates into 3D using the pinhole camera model with the LiDAR depth map.
3. **Fuse** into a single point cloud, then convert to object bounding boxes or slot occupancy vectors.

## Digital Twin Storage Model

Use a hybrid store:

* **Relational + Spatial** for structured data and fast 3D proximity search.
* **Vector indexing** for similarity search over 3D embeddings.

### Example (PostgreSQL + PostGIS)

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE inventory_items (
    sku_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    part_number VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    dimensions_vector BOX3D,
    weight_kg DECIMAL(10, 2),
    velocity_score INT
);

CREATE TABLE warehouse_zones (
    zone_id SERIAL PRIMARY KEY,
    zone_name VARCHAR(20),
    boundary_3d geometry,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE storage_slots (
    slot_id SERIAL PRIMARY KEY,
    zone_id INT REFERENCES warehouse_zones(zone_id),
    coordinate_vector POINTZ,
    volume_m3 DECIMAL(10, 4),
    status VARCHAR(20) DEFAULT 'EMPTY'
);

CREATE TABLE live_inventory_locations (
    instance_id SERIAL PRIMARY KEY,
    sku_id UUID REFERENCES inventory_items(sku_id),
    slot_id INT REFERENCES storage_slots(slot_id),
    last_detected_by_machine_id VARCHAR(50),
    last_sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Optimization Heuristics

A default **Smart Put-Away** heuristic can be encoded as a weighted cost function:

```
Score = wD * DistanceToDock + wV * VelocityPenalty + wS * StabilityPenalty + wC * CompatibilityPenalty
```

**Recommendations:**

- **Distance (D):** Minimize for fast movers.
- **Velocity (V):** Higher velocity gets lower cost in the “golden zone.”
- **Stability (S):** Heavy items prioritize lower Z to reduce risk.
- **Compatibility (C):** Block incompatible materials or zone exclusions.

### Example Pseudocode (ROS 2)

```python
class WarehouseTwinNode(rclpy.node.Node):
    def __init__(self):
        super().__init__('warehouse_twin_sync')
        self.lidar_sub = self.create_subscription(PointCloud2, '/machine_1/lidar', self.sync_callback, 10)
        self.video_sub = self.create_subscription(Image, '/machine_1/camera', self.sync_callback, 10)
        self.twin = DigitalTwin()
        self.optimizer = SpaceOptimizer()

    def sync_callback(self, lidar_msg, img_msg):
        point_cloud_3d = self.fuse_sensors(lidar_msg, img_msg)
        self.twin.update_vector_map(point_cloud_3d)
        for order in self.get_pending_orders():
            best_slot = self.optimizer.find_best_fit(order, self.twin.get_free_space())
            self.twin.allocate_space(order, best_slot)
```

## Operational Considerations

- **Latency-first design:** prefer UDP or WebRTC for video, gRPC for point cloud packets.
- **SLAM integration:** use LIO-SAM or similar for spatial localization without GPS.
- **Edge preprocessing:** downsample LiDAR before transmission to conserve bandwidth.
- **State management:** ensure the twin’s updates are idempotent and replayable (e.g., Kafka with versioned events).
