import random
import matplotlib.pyplot as plt

ROAD_LENGTH = 100.0
MERGE_POINT = 70.0
SAFE_DISTANCE = 2.0
MAX_V_SPEED = 3.0

class Vehicle:
    def __init__(self, v_id, lane, init_pos, driver_type):
        self.id = v_id
        self.lane = lane # 0 for left, 1 for right
        self.position = init_pos
        self.speed = MAX_V_SPEED
        self.driver_type = driver_type
        self.passed = False
        self.wait_time = 0
        self.finished = False

    def get_gap(self, vehicle_ahead):
        if not vehicle_ahead:
            return float('inf')
        return vehicle_ahead.position - self.position - SAFE_DISTANCE

    def update_speed(self, vehicle_ahead, stop_for_merge):
        gap = self.get_gap(vehicle_ahead)
        
        if stop_for_merge:
            gap = min(gap, MERGE_POINT - self.position - SAFE_DISTANCE)
            
        if gap < 0:
            self.speed = 0
            self.wait_time += 1
        elif gap < self.speed:
            self.speed = max(0, gap) # brake to avoid collision
            if self.speed < MAX_V_SPEED * 0.1:
                self.wait_time += 1
        else:
            self.speed = min(MAX_V_SPEED, self.speed + 0.5) # accelerate

    def move(self):
        self.position += self.speed
        if self.position >= ROAD_LENGTH:
            self.finished = True
        elif self.position >= MERGE_POINT:
            self.passed = True
            self.lane = 0 # post-merge, everyone is in lane 0

class Road:
    def __init__(self):
        self.lanes = {0: [], 1: []}
        self.passed_vehicles = []
        
    def add_vehicle(self, v):
        self.lanes[v.lane].append(v)
        
    def get_vehicle_ahead(self, v, target_lane=None):
        search_lane = target_lane if target_lane is not None else v.lane
        ahead = None
        min_dist = float('inf')
        
        # Check vehicles in target lane
        for other in self.lanes[search_lane]:
            dist = other.position - v.position
            if 0 < dist < min_dist:
                min_dist = dist
                ahead = other
                
        # Also check passed vehicles (which are functionally in lane 0)
        # Even if we are in lane 1, a passed vehicle might be right in front of the merge point.
        for other in self.passed_vehicles:
             dist = other.position - v.position
             if 0 < dist < min_dist:
                 min_dist = dist
                 ahead = other
                 
        return ahead

    def get_vehicle_behind(self, v, target_lane):
        behind = None
        min_dist = float('inf')
        for other in self.lanes[target_lane]:
            dist = v.position - other.position
            if 0 < dist < min_dist:
                min_dist = dist
                behind = other
        # Passed vehicles are by definition ahead, so they can't be behind.
        return behind

    def move_vehicle_lane(self, v, new_lane):
        self.lanes[v.lane].remove(v)
        v.lane = new_lane
        self.lanes[new_lane].append(v)


class Simulation:
    def __init__(self, strategy='baseline', num_vehicles=60, agg_ratio=0.3):
        self.strategy = strategy
        self.num_vehicles = num_vehicles
        self.road = Road()
        self.step_count = 0
        self.queue_lengths = []
        self.throughput_count = 0
        self.spawned = 0
        self.all_vehicles = []
        
        # For zipper merge
        self.last_merged_lane = random.choice([0, 1])

        # Generate vehicle schedule
        self.spawn_schedule = []
        for i in range(num_vehicles):
            driver_type = 'aggressive' if random.random() < agg_ratio else 'disciplined'
            lane = random.choice([0, 1])
            self.spawn_schedule.append({'id': i, 'lane': lane, 'driver_type': driver_type})

    def run(self, max_steps=1000):
        while not self.is_finished() and self.step_count < max_steps:
            self.step()
        self.calculate_metrics()

    def is_finished(self):
        return self.spawned == self.num_vehicles and \
               len(self.road.lanes[0]) == 0 and \
               len(self.road.lanes[1]) == 0 and \
               all(v.finished for v in self.road.passed_vehicles)

    def spawn_vehicles(self):
        # Spawn randomly 1 or 2 cars if space permits at the start of road
        if self.spawned < self.num_vehicles:
            if random.random() < 0.4: # Spawn probability
                info = self.spawn_schedule[self.spawned]
                # Check space at start of lane
                start_space_clear = True
                for v in self.road.lanes[info['lane']]:
                    if v.position < SAFE_DISTANCE * 2:
                        start_space_clear = False
                
                if start_space_clear:
                    new_v = Vehicle(info['id'], info['lane'], 0.0, info['driver_type'])
                    self.road.add_vehicle(new_v)
                    self.all_vehicles.append(new_v)
                    self.spawned += 1

    def handle_baseline_merges(self):
        for lane in [0, 1]:
            for v in list(self.road.lanes[lane]):
                if v.passed: continue
                dist_to_merge = MERGE_POINT - v.position
                
                # Disciplined drivers in lane 1 try to merge early
                if lane == 1 and v.driver_type == 'disciplined' and 10 < dist_to_merge < 40:
                    ahead = self.road.get_vehicle_ahead(v, target_lane=0)
                    behind = self.road.get_vehicle_behind(v, target_lane=0)
                    # Merge if enough gap
                    gap_ahead = (ahead.position - v.position) if ahead else float('inf')
                    gap_behind = (v.position - behind.position) if behind else float('inf')
                    
                    if gap_ahead > SAFE_DISTANCE * 1.5 and gap_behind > SAFE_DISTANCE * 1.5:
                        self.road.move_vehicle_lane(v, 0)
                
                # Baseline merge near the point
                if dist_to_merge < SAFE_DISTANCE * 2 and lane == 1:
                    ahead = self.road.get_vehicle_ahead(v, target_lane=0)
                    behind = self.road.get_vehicle_behind(v, target_lane=0)
                    gap_ahead = (ahead.position - v.position) if ahead else float('inf')
                    gap_behind = (v.position - behind.position) if behind else float('inf')
                    
                    if gap_ahead > SAFE_DISTANCE and gap_behind > SAFE_DISTANCE:
                        self.road.move_vehicle_lane(v, 0)
                        
    def handle_zipper_merges(self):
        # Identify vehicles exactly at the merge point (within 2x SAFE_DISTANCE)
        at_merge = {0: [], 1: []}
        for lane in [0, 1]:
            for v in self.road.lanes[lane]:
                if v.passed: continue
                # In zipper, everyone stays in their lane until the end
                if MERGE_POINT - v.position < SAFE_DISTANCE * 3:
                     at_merge[lane].append(v)
                     
        # Sort those near merge by position (front first)
        at_merge[0].sort(key=lambda x: x.position, reverse=True)
        at_merge[1].sort(key=lambda x: x.position, reverse=True)
        
        # If both lanes have a car waiting to merge
        if at_merge[0] and at_merge[1]:
            v0 = at_merge[0][0]
            v1 = at_merge[1][0]
            
            # The right of way switches
            target_lane_turn = 1 - self.last_merged_lane
            
            if target_lane_turn == 1:
                # Merge lane 1 into 0
                ahead_0 = self.road.get_vehicle_ahead(v1, target_lane=0)
                if not ahead_0 or (ahead_0.position - MERGE_POINT > SAFE_DISTANCE):
                    self.road.move_vehicle_lane(v1, 0)
                    self.last_merged_lane = 1
            else:
                # Let lane 0 proceed past merge
                # We don't change lane, they are already in 0
                ahead_0 = self.road.get_vehicle_ahead(v0)
                if not ahead_0 or (ahead_0.position - v0.position > SAFE_DISTANCE):
                     self.last_merged_lane = 0
                
        elif at_merge[0] and not at_merge[1]:
             self.last_merged_lane = 0
        elif at_merge[1] and not at_merge[0]:
             # Merge lane 1
             v1 = at_merge[1][0]
             ahead_0 = self.road.get_vehicle_ahead(v1, target_lane=0)
             if not ahead_0 or (ahead_0.position - MERGE_POINT > SAFE_DISTANCE):
                 self.road.move_vehicle_lane(v1, 0)
                 self.last_merged_lane = 1

    def step(self):
        self.spawn_vehicles()
        
        # Determine merge actions
        if self.strategy == 'baseline':
            self.handle_baseline_merges()
        elif self.strategy == 'zipper':
            self.handle_zipper_merges()
            
        # Update speeds and positions
        for lane in [0, 1]:
            for v in self.road.lanes[lane]:
                ahead = self.road.get_vehicle_ahead(v)
                
                stop_for_merge = False
                if lane == 1 and not v.passed:
                    stop_for_merge = True

                # In baseline, aggressive drivers force way in, but for simulation stability,
                # they just stop and wait at the merge point until a gap appears.
                v.update_speed(ahead, stop_for_merge=stop_for_merge)
                v.move()
                
        # Handle passed vehicles (technically all now in lane 0 beyond merge)
        passed_remove = []
        for v in self.road.passed_vehicles:
            # For a passed vehicle, it's in a single lane.
            # Its 'ahead' vehicle could be further down the road.
            min_dist = float('inf')
            ahead = None
            for other in self.road.passed_vehicles:
                if other != v and other.position > v.position:
                    if other.position - v.position < min_dist:
                        min_dist = other.position - v.position
                        ahead = other
            v.update_speed(ahead, stop_for_merge=False)
            v.move()
            if v.finished:
                self.throughput_count += 1
                passed_remove.append(v)
                
        # Clean up lists
        for v in passed_remove:
            self.road.passed_vehicles.remove(v)
            
        # Promote any newly passed vehicles
        for lane in [0, 1]:
            promote = [v for v in self.road.lanes[lane] if v.passed]
            for v in promote:
                self.road.lanes[lane].remove(v)
                self.road.passed_vehicles.append(v)
                
        # Record queue length
        queue_len = sum(1 for ln in self.road.lanes.values() for v in ln if v.speed < MAX_V_SPEED * 0.2)
        self.queue_lengths.append(queue_len)
        self.step_count += 1

    def calculate_metrics(self):
        self.avg_wait_time = sum(v.wait_time for v in self.all_vehicles) / len(self.all_vehicles)
        self.throughput = self.num_vehicles / self.step_count if self.step_count > 0 else 0
        self.max_queue = max(self.queue_lengths) if self.queue_lengths else 0
        self.avg_queue = sum(self.queue_lengths) / len(self.queue_lengths) if self.queue_lengths else 0

def run_comparisons():
    print("Running Baseline Simulation...")
    baseline_sim = Simulation(strategy='baseline')
    baseline_sim.run()
    
    print("Running Zipper Merge Simulation...")
    zipper_sim = Simulation(strategy='zipper')
    # Copy vehicles exactly to ensure fairness
    zipper_sim.spawn_schedule = baseline_sim.spawn_schedule
    zipper_sim.run()

    # --- Print Results ---
    print("\n--- Simulation Results ---")
    print(f"Total Vehicles: {baseline_sim.num_vehicles}")
    print("\nBaseline Merging:")
    print(f"  Average Wait Time: {baseline_sim.avg_wait_time:.2f} steps")
    print(f"  Throughput: {baseline_sim.throughput:.4f} veh/step")
    print(f"  Max Queue Length: {baseline_sim.max_queue} vehicles")
    print(f"  Average Queue Length: {baseline_sim.avg_queue:.2f} vehicles")
    
    print("\nZipper Merging:")
    print(f"  Average Wait Time: {zipper_sim.avg_wait_time:.2f} steps")
    print(f"  Throughput: {zipper_sim.throughput:.4f} veh/step")
    print(f"  Max Queue Length: {zipper_sim.max_queue} vehicles")
    print(f"  Average Queue Length: {zipper_sim.avg_queue:.2f} vehicles")

    # --- Plotting ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 1. Wait Times Comparison (Bar)
    labels = ['Baseline', 'Zipper Merge']
    wait_times = [baseline_sim.avg_wait_time, zipper_sim.avg_wait_time]
    axes[0].bar(labels, wait_times, color=['salmon', 'skyblue'])
    axes[0].set_title('Average Wait Time per Vehicle')
    axes[0].set_ylabel('Wait Time (Simulation Steps)')
    
    # 2. Queue Length Over Time (Line)
    axes[1].plot(baseline_sim.queue_lengths, label='Baseline', color='salmon', alpha=0.7)
    axes[1].plot(zipper_sim.queue_lengths, label='Zipper Merge', color='skyblue', alpha=0.7)
    axes[1].set_title('Queue Length Over Time')
    axes[1].set_xlabel('Simulation Step')
    axes[1].set_ylabel('Number of Queued Vehicles')
    axes[1].legend()

    # 3. Throughput (Bar)
    throughputs = [baseline_sim.throughput, zipper_sim.throughput]
    axes[2].bar(labels, throughputs, color=['salmon', 'skyblue'])
    axes[2].set_title('System Throughput')
    axes[2].set_ylabel('Vehicles per Step')

    plt.tight_layout()
    plt.savefig('comparison_results.png')
    print("\nSaved comparison plots to 'comparison_results.png'.")
    plt.show()

if __name__ == "__main__":
    run_comparisons()
