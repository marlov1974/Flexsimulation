# Design principles

## 1. Business case first

The simulator exists to compare capability scenarios and quantify incremental value. Physical realism is useful only when it improves the business-case answer.

## 2. Reality proxy, not model leakage

The simulator may contain latent household, person, device and behaviour state. ML and bidding models must only see observations exposed by the observation layer.

## 3. Plans are first-class objects

15-minute baseline plans and activation plans are core concepts. Flexibility is measured as a controlled deviation from a plan, not as a vague change from historical behaviour.

## 4. Rebound is explicit

Any deferred or advanced energy creates a rebound position with energy, deadline, power limit, cost and market implications.

## 5. Cross-asset effects matter

Assets should not only be valued separately. The simulator must be able to show how one resource improves or worsens the value of another resource.

## 6. Capabilities are selectable

System capabilities and edge capabilities should be separable so scenarios can include or exclude them.

## 7. Synthetic and neutral

Use synthetic examples and neutral terms. Do not store real customer, commercial or proprietary information.
