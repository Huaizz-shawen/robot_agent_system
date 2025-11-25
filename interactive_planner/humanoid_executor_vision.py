# humanoid_executor_vision.py

"""
Vision-Enabled Humanoid Robot Executor
Extends HumanoidExecutor with vision-based observation capabilities
"""

import os
from typing import Dict, Any, Optional
from humanoid_executor import HumanoidExecutor, ExecutionResult
from qwen_vlm_client import QwenVLMClient
from simulation_image_manager import SimulationImageManager


class VisionEnabledExecutor(HumanoidExecutor):
    """
    Vision-enabled executor for Unitree-G1 Humanoid Robot

    Extends base executor with:
    - Automatic visual observation capture
    - VLM-based action verification
    - State-aware image management
    """

    def __init__(self,
                 simulation_mode: bool = True,
                 verbose: bool = True,
                 enable_vision: bool = True,
                 vlm_model: str = "qwen-vl-plus"):
        """
        Initialize vision-enabled executor

        Args:
            simulation_mode: If True, use simulation; if False, use real hardware
            verbose: Print execution details
            enable_vision: Enable vision-based observation
            vlm_model: VLM model to use (qwen-vl-plus, qwen-vl-max)
        """
        # Initialize base executor
        super().__init__(simulation_mode=simulation_mode, verbose=verbose)

        self.enable_vision = enable_vision
        self.vlm_model = vlm_model

        # Vision components
        self.vlm_client = None
        self.image_manager = None

        if enable_vision:
            self._initialize_vision_system()

    def _initialize_vision_system(self):
        """Initialize vision components"""
        try:
            # Initialize VLM client
            if os.getenv("DASHSCOPE_API_KEY"):
                self.vlm_client = QwenVLMClient(
                    model_name=self.vlm_model,
                    verbose=self.verbose
                )
                if self.verbose:
                    print(f"✅ VLM client initialized: {self.vlm_model}")
            else:
                if self.verbose:
                    print("⚠️  DASHSCOPE_API_KEY not set. VLM disabled (will use text descriptions)")
                self.enable_vision = False

            # Initialize simulation image manager (always available)
            self.image_manager = SimulationImageManager(
                image_directory="simulation_images",
                verbose=self.verbose
            )

        except Exception as e:
            if self.verbose:
                print(f"⚠️  Vision system initialization failed: {str(e)}")
                print("   Falling back to text-only mode")
            self.enable_vision = False

    def execute_action(self, action_type: str, action_name: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """
        Execute action with vision-based observation

        Flow:
        1. Capture observation BEFORE action (if using vision)
        2. Execute action using base executor
        3. Capture observation AFTER action
        4. Use VLM to analyze result (if enabled)
        5. Return enhanced ExecutionResult

        Args:
            action_type: Type of action (talk, tool, act, sense)
            action_name: Specific action name
            parameters: Action parameters

        Returns:
            ExecutionResult with visual observation data
        """
        # Execute using base executor
        base_result = super().execute_action(action_type, action_name, parameters)

        # Add vision-based observation if image manager is available
        if self.image_manager:
            # Get observation image after action
            observation_image = self.image_manager.get_observation_after_action(
                action_type,
                action_name,
                parameters
            )

            # Add image path to result data
            base_result.data['observation_image'] = observation_image
            base_result.data['state'] = self.image_manager.state.copy()

            # Optionally, use VLM to get observation if API is available
            if self.vlm_client and os.path.exists(observation_image):
                try:
                    vlm_observation = self.vlm_client.get_observation_description(observation_image)
                    # Store VLM observation in data for planner to use
                    base_result.data['vlm_observation'] = vlm_observation
                    # Don't add to feedback - it's too verbose for display
                    # The planner will see it via the image directly

                except Exception as e:
                    if self.verbose:
                        print(f"⚠️  VLM observation failed: {str(e)}")
                    # Continue with base feedback

        return base_result

    def get_current_observation(self) -> Dict[str, Any]:
        """
        Get current visual observation

        Returns:
            dict: {
                'image_path': str,
                'state': dict,
                'vlm_description': str (if VLM enabled)
            }
        """
        if not self.image_manager:
            return {
                'image_path': None,
                'state': {},
                'vlm_description': 'Vision system not initialized'
            }

        observation_image = self.image_manager.get_current_observation_image()

        observation_data = {
            'image_path': observation_image,
            'state': self.image_manager.state.copy(),
            'vlm_description': None
        }

        # Get VLM description if available
        if self.vlm_client and os.path.exists(observation_image):
            try:
                vlm_desc = self.vlm_client.get_observation_description(observation_image)
                observation_data['vlm_description'] = vlm_desc
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  VLM observation failed: {str(e)}")

        return observation_data

    def register_custom_observation_image(self, state_key: str, image_path: str):
        """
        Register a custom observation image for a specific state

        Args:
            state_key: State identifier (e.g., "home_ac_on_22")
            image_path: Path to image file
        """
        if self.image_manager:
            self.image_manager.register_custom_image(state_key, image_path)
        else:
            print("⚠️  Image manager not initialized")

    def reset_vision_state(self):
        """Reset vision system state"""
        if self.image_manager:
            self.image_manager.reset_state()

    def get_vision_statistics(self) -> Dict:
        """Get vision system statistics"""
        stats = {
            'vision_enabled': self.enable_vision,
            'vlm_model': self.vlm_model if self.vlm_client else None,
            'vlm_available': self.vlm_client is not None,
        }

        if self.image_manager:
            stats['state_summary'] = self.image_manager.get_state_summary()

        return stats


# Example usage
if __name__ == "__main__":
    print("🤖 Vision-Enabled Humanoid Executor - Test Mode\n")

    # Test with simulation mode
    print("="*70)
    print("Initializing Vision-Enabled Executor (Simulation Mode)")
    print("="*70)

    executor = VisionEnabledExecutor(
        simulation_mode=True,
        verbose=True,
        enable_vision=True
    )

    # Test action execution with vision
    print("\n" + "="*70)
    print("Test 1: Get Current Observation")
    print("="*70)
    obs = executor.get_current_observation()
    print(f"Observation Image: {obs['image_path']}")
    print(f"Current State: {obs['state']}")

    print("\n" + "="*70)
    print("Test 2: Execute Action (Turn on AC)")
    print("="*70)
    result = executor.execute_action("tool", "control_air_conditioner", {
        "action": "turn_on",
        "temperature": 22
    })
    print(f"Success: {result.success}")
    print(f"Feedback: {result.feedback}")
    print(f"Observation Image: {result.data.get('observation_image')}")
    print(f"New State: {result.data.get('state')}")

    print("\n" + "="*70)
    print("Test 3: Get Observation After Action")
    print("="*70)
    obs_after = executor.get_current_observation()
    print(f"Observation Image: {obs_after['image_path']}")
    print(f"Current State: {obs_after['state']}")

    # Show statistics
    print("\n" + "="*70)
    print("Vision System Statistics")
    print("="*70)
    import json
    stats = executor.get_vision_statistics()
    print(json.dumps(stats, indent=2))

    print("\n" + "="*70)
    print("Execution Complete")
    print("="*70)
    print("\nTo use with real VLM:")
    print("  1. Set DASHSCOPE_API_KEY environment variable")
    print("  2. Provide real observation images in simulation_images/")
    print("  3. VLM will automatically analyze images and enhance feedback")
    print("="*70)
