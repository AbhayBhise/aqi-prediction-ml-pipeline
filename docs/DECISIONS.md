# BreatheWise Architecture Decisions

This document records the major architectural and design decisions made during the transition from Version 1 (AQI ML Vision) to Version 2 (BreatheWise). These decisions reflect a shift from an academic predictive modeling exercise to a production-grade personal environmental intelligence platform.

---

### Decision #1: Why PostgreSQL + TimescaleDB (abstracted via SQLAlchemy) instead of purely direct SQLite?
**Context:** The application needs to store and query millions of rows of environmental time-series data.
**Decision:** We abstracted the data layer using SQLAlchemy. While SQLite is used for MVP local execution, the architecture natively supports scaling to PostgreSQL and TimescaleDB via connection strings.
**Reasoning:** Air quality ingestion is inherently a time-series problem. TimescaleDB extends PostgreSQL to handle massive time-series operations (aggregations, downsampling, moving averages) efficiently at scale, preventing the severe I/O bottlenecks experienced in V1's eager CSV loading.

### Decision #2: Why build a Data Provider Abstraction?
**Context:** We initially fetched data from OpenWeather.
**Decision:** We created an `AQIDataProvider` interface, wrapping OpenWeather and WAQI, allowing seamless swapping of backend providers.
**Reasoning:** External APIs fail, deprecate endpoints, or implement rate limits. A monolithic app breaks when its single provider breaks. This abstraction ensures we can silently fall back to WAQI, CPCB, or IMD without rewriting our ingestion, caching, or ML pipelines.

### Decision #3: Why Continuous Regression over Classification?
**Context:** V1 categorized AQI purely into buckets (Good, Moderate, Unhealthy).
**Decision:** V2's ML engine forecasts raw, continuous PM2.5/AQI values. The Decision Engine then categorizes the output downstream.
**Reasoning:** Continuous regression preserves data resolution. If an AQI moves from 151 (Unhealthy) to 199 (Unhealthy), a classifier sees no change. A regressor captures this 30% worsening, allowing us to generate high-fidelity Exposure Indexes and hyper-optimized commute recommendations.

### Decision #4: Why the Exposure Index instead of an arbitrary "Budget"?
**Context:** We wanted to gamify pollution exposure tracking.
**Decision:** We introduced the Exposure Index: a mathematically rigorous backend formula `f(Predicted PM2.5, Duration, WHO guideline, User sensitivity multiplier, Activity intensity)` mapped to a user-friendly 0-100 frontend score.
**Reasoning:** It converts arbitrary air quality numbers into scientifically grounded, personalized risk thresholds. This makes the product defensible to investors, medical professionals, and B2B clients, shifting the app from an "AQI dashboard" to a "lifestyle risk manager."

### Decision #5: Why focus on the "Daily Air Plan" instead of scattered widgets?
**Context:** V1 featured a dashboard of scattered metrics, charts, and recommendations.
**Decision:** V2 consolidates the user experience into a single, proactive "Daily Air Plan" (e.g., "Open windows at 6 AM, delay commute until 9 AM").
**Reasoning:** Users don't care about AQI digits; they care about *decisions*. By generating a unified daily schedule, we solve the user's immediate problem with zero cognitive load, which is the ultimate hallmark of a successful consumer AI product.
