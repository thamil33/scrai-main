# Memory Consolidator Design

## Trigger Logic

The memory consolidator will be triggered by a combination of event count and time-based intervals. This hybrid approach ensures that memory is processed both during periods of high activity and during lulls.

### Event Count Trigger

- **Threshold:** The consolidator will trigger after a set number of `WorldStateCommittedEvent`s have been processed. This threshold will be configurable.
- **Rationale:** This ensures that memory is updated frequently during active simulations, providing agents with timely information.

### Time-Based Trigger

- **Interval:** The consolidator will trigger at a regular, configurable interval (e.g., every 5 minutes).
- **Rationale:** This guarantees that memory is processed even when there are no new events, which is important for long-term memory consolidation and reflection.

## Implementation

The memory consolidator will be implemented as a separate system that subscribes to the `world_state_committed_events` stream. It will maintain an internal buffer of events and, when a trigger condition is met, it will process the buffered events to generate higher-level memories and insights.
