import random
import matplotlib.pyplot as plt # Assuming matplotlib is available or user installs it
from typing import List

class FissionSimulator:
    """
    Fission Simulation Utility.
    Simulates activations over 15 hops with configurable k.
    """
    
    def simulate_chain(self, initial_neutrons: int, k_target: float, hops: int = 15) -> List[int]:
        """
        Runs a simulation of population growth/decay.
        """
        population = [initial_neutrons]
        current = initial_neutrons
        
        for _ in range(hops):
            # Apply some noise to k
            noise = random.uniform(-0.1, 0.1)
            effective_k = max(0, k_target + noise)
            
            # Control Rods: Cap at reasonable max (e.g. 1000) to prevent overflow in sim
            if current > 1000:
                effective_k = 0.5 # SCRAM
                
            next_gen = int(current * effective_k)
            population.append(next_gen)
            current = next_gen
            
        return population

    def run_scenarios(self):
        """
        Runs scenarios for k=0.8, 1.0, 1.2 and saves/prints output.
        """
        scenarios = [0.8, 1.0, 1.2]
        results = {}
        
        print("--- Fission Simulation Results ---")
        for k in scenarios:
            seq = self.simulate_chain(100, k)
            results[k] = seq
            print(f"k={k}: {seq}")
            
        return results

if __name__ == "__main__":
    sim = FissionSimulator()
    sim.run_scenarios()
