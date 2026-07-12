import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """SQLAlchemy Declarative Base class."""
    pass

class ProductConfig(Base):
    """Database ORM for product specific prompts and token budgets configuration."""
    __tablename__ = "product_configs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, comment="Product key identifier (e.g. english_coach).")
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    prompt_template: Mapped[str] = mapped_column(Text)
    max_dynamic_tokens: Mapped[int] = mapped_column(default=500)

class LearnerProfile(Base):
    """Database ORM storing Prakash's general preferences and profile summaries."""
    __tablename__ = "learner_profiles"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, comment="Unique composite key or user_id.")
    user_id: Mapped[str] = mapped_column(String(100))
    tenant_id: Mapped[str] = mapped_column(String(50), default="default_tenant", server_default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    summary: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, comment="JSON formatted key-value settings.")

class Session(Base):
    """Database ORM representing active chat session tracks."""
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100))
    tenant_id: Mapped[str] = mapped_column(String(50), default="default_tenant", server_default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    """Database ORM representing single chat messages with token audit records."""
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"))
    role: Mapped[str] = mapped_column(String(20)) # system, user, assistant
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, comment="Structured latency, cost, and tags details.")

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="messages")

class ApprovedExample(Base):
    """Database ORM representing validated example corrections for prompt injects."""
    __tablename__ = "approved_examples"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(50))
    input_text: Mapped[str] = mapped_column(Text)
    natural_english: Mapped[str] = mapped_column(Text)
    professional_english: Mapped[str] = mapped_column(Text)
    tags_json: Mapped[str] = mapped_column(Text, comment="JSON array of tags.")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class FamilyProfile(Base):
    """Database ORM for family member check-in config states and escalation contacts."""
    __tablename__ = "family_profiles"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, comment="The user_id.")
    parent_name: Mapped[str] = mapped_column(String(100))
    tenant_id: Mapped[str] = mapped_column(String(50), default="default_tenant", server_default="default_tenant")
    preferred_language: Mapped[str] = mapped_column(String(50), default="English")
    escalation_contacts_json: Mapped[str] = mapped_column(Text, comment="JSON structured name/phone list.")
    script_stage: Mapped[str] = mapped_column(String(50), default="start")

class CheckinRun(Base):
    """Database ORM storing check-in wellness triggers and manual alerts."""
    __tablename__ = "checkin_runs"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100))
    tenant_id: Mapped[str] = mapped_column(String(50), default="default_tenant", server_default="default_tenant")
    session_id: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="normal") # normal, flagged, escalated
    escalated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)

class TaskRun(Base):
    """Database ORM mapping Celery task execution states, retries, and failure reasons."""
    __tablename__ = "task_runs"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    task_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="PENDING")  # PENDING, STARTED, SUCCESS, FAILURE
    retries: Mapped[int] = mapped_column(default=0)
    duration_ms: Mapped[float] = mapped_column(default=0.0)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

class Organization(Base):
    """Database ORM representing a SaaS workspace organization."""
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class Tenant(Base):
    """Database ORM representing a SaaS tenant partition with specific plans and caps."""
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    org_id: Mapped[str] = mapped_column(String(100), ForeignKey("organizations.id"))
    plan_tier: Mapped[str] = mapped_column(String(50), default="free")  # free, growth, enterprise
    monthly_budget_usd: Mapped[float] = mapped_column(default=100.0)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class Membership(Base):
    """Database ORM mapping SaaS users to tenants with specific roles."""
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), ForeignKey("tenants.id"))
    user_id: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50), default="user")  # user, admin
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class ProductEntitlement(Base):
    """Database ORM gating which SaaS features or coaches are active for a tenant."""
    __tablename__ = "product_entitlements"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), ForeignKey("tenants.id"))
    product_id: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class UsageLedger(Base):
    """Database ORM logging token counts and estimated costs for SaaS billing metrics."""
    __tablename__ = "usage_ledger"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), ForeignKey("tenants.id"))
    product_id: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[str] = mapped_column(String(100))
    token_input: Mapped[int] = mapped_column(default=0)
    token_output: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class ReviewQueue(Base):
    """Database ORM tracking human-in-the-loop approvals, escalations, and overrides."""
    __tablename__ = "review_queue"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(100))
    trace_id: Mapped[Optional[str]] = mapped_column(String(100))
    tenant_id: Mapped[str] = mapped_column(String(100))
    product_id: Mapped[str] = mapped_column(String(50))
    input_text: Mapped[str] = mapped_column(Text)
    original_response: Mapped[Optional[str]] = mapped_column(Text)
    edited_response: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="PENDING")  # PENDING, APPROVED, REJECTED, RESOLVED
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100))
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class PromptVersion(Base):
    """Database ORM versioning system and context templates for routing configurations."""
    __tablename__ = "prompt_versions"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(50))
    task_id: Mapped[str] = mapped_column(String(50))
    version: Mapped[str] = mapped_column(String(50))  # e.g., v1.0
    prompt_template: Mapped[str] = mapped_column(Text)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class Experiment(Base):
    """Database ORM mapping prompt templates variations and A/B test allocation splits."""
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    prompt_version_id: Mapped[str] = mapped_column(String(100), ForeignKey("prompt_versions.id"))
    weight: Mapped[float] = mapped_column(default=0.5)  # A/B test split allocation
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class KnowledgeDocument(Base):
    """Database ORM mapping ingested knowledge documents."""
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100))
    product_id: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(100))
    source_type: Mapped[str] = mapped_column(String(50))  # jsonl, csv, md, pdf
    metadata_json: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class KnowledgeChunk(Base):
    """Database ORM mapping document text chunks and embeddings."""
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(100), ForeignKey("knowledge_documents.id"))
    tenant_id: Mapped[str] = mapped_column(String(100))
    product_id: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    embedding_json: Mapped[str] = mapped_column(Text, comment="JSON representation of float array embedding.")
    metadata_json: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class RetrievalLog(Base):
    """Database ORM recording queries, retrieved context chunks, and scores."""
    __tablename__ = "retrieval_logs"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100))
    product_id: Mapped[str] = mapped_column(String(50))
    query_text: Mapped[str] = mapped_column(Text)
    retrieved_chunks_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class FeedbackExample(Base):
    """Database ORM persisting human-approved/rejected flywheel examples."""
    __tablename__ = "feedback_examples"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100))
    product_id: Mapped[str] = mapped_column(String(50))
    input_text: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="positive")  # positive, negative
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class Dataset(Base):
    """Database ORM representing registered ingestion datasets."""
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100))
    product_id: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(100))
    version: Mapped[str] = mapped_column(String(50))
    file_path: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="PENDING")  # PENDING, INGESTED, ERROR, DISABLED
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class BenchmarkManifest(Base):
    """Database ORM tracking external benchmark dataset metadata and license constraints."""
    __tablename__ = "benchmark_manifests"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(100))
    source_url: Mapped[str] = mapped_column(String(500))
    split: Mapped[str] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(50))
    license: Mapped[str] = mapped_column(String(200))
    intended_use: Mapped[str] = mapped_column(String(255))
    commercial_restriction: Mapped[bool] = mapped_column(Boolean, default=True)
    ingestion_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    max_examples: Mapped[int] = mapped_column(default=1000)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class BatchEvalRun(Base):
    """Database ORM tracking large-scale evaluation run execution state and costs."""
    __tablename__ = "batch_eval_runs"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(100))
    tenant_id: Mapped[str] = mapped_column(String(100), default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="PENDING")  # PENDING, RUNNING, COMPLETED, BUDGET_STOPPED, FAILED
    total_examples: Mapped[int] = mapped_column(default=0)
    processed_count: Mapped[int] = mapped_column(default=0)
    passed_count: Mapped[int] = mapped_column(default=0)
    failed_count: Mapped[int] = mapped_column(default=0)
    total_tokens: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)
    budget_limit_usd: Mapped[float] = mapped_column(default=5.0)
    avg_score: Mapped[float] = mapped_column(default=0.0)
    model_name: Mapped[str] = mapped_column(String(100), default="mock")
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50))
    checkpoint_json: Mapped[Optional[str]] = mapped_column(Text, comment="JSON checkpoint for resumable runs.")
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class EvalExampleResult(Base):
    """Database ORM storing per-example evaluation outputs with cost and quality metrics."""
    __tablename__ = "eval_example_results"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(100), ForeignKey("batch_eval_runs.id"))
    example_hash: Mapped[str] = mapped_column(String(64), comment="SHA-256 content hash for dedup.")
    task_type: Mapped[str] = mapped_column(String(50))  # correction, translation, intent_routing
    input_text: Mapped[str] = mapped_column(Text)
    reference_text: Mapped[Optional[str]] = mapped_column(Text)
    model_output: Mapped[Optional[str]] = mapped_column(Text)
    composite_score: Mapped[float] = mapped_column(default=0.0)
    scores_json: Mapped[Optional[str]] = mapped_column(Text, comment="JSON per-dimension score breakdown.")
    model_name: Mapped[str] = mapped_column(String(100), default="mock")
    tokens_used: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)
    latency_ms: Mapped[float] = mapped_column(default=0.0)
    error_bucket: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="PENDING")  # PENDING, SCORED, PROMOTED, REJECTED
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class ErrorCluster(Base):
    """Database ORM aggregating evaluation failures into labelled error buckets."""
    __tablename__ = "error_clusters"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(100), ForeignKey("batch_eval_runs.id"))
    bucket_name: Mapped[str] = mapped_column(String(50))
    count: Mapped[int] = mapped_column(default=0)
    dataset_name: Mapped[str] = mapped_column(String(100))
    model_name: Mapped[str] = mapped_column(String(100))
    product_id: Mapped[str] = mapped_column(String(50))
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class GoldExample(Base):
    """Database ORM storing quality-verified gold training examples with full provenance."""
    __tablename__ = "gold_examples"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    task_type: Mapped[str] = mapped_column(String(50))
    input_text: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str] = mapped_column(Text)
    composite_score: Mapped[float] = mapped_column(default=0.0)
    source_dataset: Mapped[str] = mapped_column(String(100))
    source_example_hash: Mapped[str] = mapped_column(String(64))
    source_run_id: Mapped[str] = mapped_column(String(100))
    promotion_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    review_status: Mapped[str] = mapped_column(String(30), default="PENDING")  # PENDING, APPROVED, REJECTED
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class HardNegativeExample(Base):
    """Database ORM storing identified hard-negative examples for contrast training."""
    __tablename__ = "hard_negative_examples"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    task_type: Mapped[str] = mapped_column(String(50))
    input_text: Mapped[str] = mapped_column(Text)
    bad_output: Mapped[str] = mapped_column(Text)
    error_bucket: Mapped[str] = mapped_column(String(50))
    composite_score: Mapped[float] = mapped_column(default=0.0)
    source_dataset: Mapped[str] = mapped_column(String(100))
    source_example_hash: Mapped[str] = mapped_column(String(64))
    source_run_id: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class LiveQualityMetric(Base):
    """Database ORM mapping rolling live quality aggregates per tenant and product."""
    __tablename__ = "live_quality_metrics"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    model_name: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(50))
    window_size: Mapped[str] = mapped_column(String(30))  # 1h, 24h, 7d
    avg_score: Mapped[float] = mapped_column(default=0.0)
    pass_rate: Mapped[float] = mapped_column(default=0.0)
    escalation_rate: Mapped[float] = mapped_column(default=0.0)
    review_queue_rate: Mapped[float] = mapped_column(default=0.0)
    budget_spend: Mapped[float] = mapped_column(default=0.0)
    token_usage: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class FailureTrend(Base):
    """Database ORM tracking failure category counts over rolling time frames."""
    __tablename__ = "failure_trends"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    error_bucket: Mapped[str] = mapped_column(String(50))
    count: Mapped[int] = mapped_column(default=0)
    window_size: Mapped[str] = mapped_column(String(30))  # 1h, 24h, 7d
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class RegressionEvent(Base):
    """Database ORM logging detected performance regressions compared to baselines."""
    __tablename__ = "regression_events"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    metric_name: Mapped[str] = mapped_column(String(100))
    baseline_value: Mapped[float] = mapped_column(default=0.0)
    current_value: Mapped[float] = mapped_column(default=0.0)
    threshold_crossed: Mapped[float] = mapped_column(default=0.0)
    severity: Mapped[str] = mapped_column(String(30), default="warning")  # warning, critical
    prompt_version: Mapped[str] = mapped_column(String(50))
    model_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")  # ACTIVE, RESOLVED, ACKNOWLEDGED
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class HardCase(Base):
    """Database ORM mapping sampled complex edge cases queued for reviewer labeling."""
    __tablename__ = "hard_case_queue"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default_tenant")
    product_id: Mapped[str] = mapped_column(String(50))
    input_text: Mapped[str] = mapped_column(Text)
    reason_sampled: Mapped[str] = mapped_column(String(255))
    priority: Mapped[int] = mapped_column(default=0)  # 0 to 5 (higher is urgent)
    confidence: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str] = mapped_column(String(30), default="PENDING")  # PENDING, REVIEWED, DISCARDED
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class ReviewerProductivity(Base):
    """Database ORM tracking reviewer throughput stats and alignment drift metrics."""
    __tablename__ = "reviewer_productivity"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    reviewer_id: Mapped[str] = mapped_column(String(100))
    tenant_id: Mapped[str] = mapped_column(String(100), default="default_tenant")
    resolutions_count: Mapped[int] = mapped_column(default=0)
    avg_duration_ms: Mapped[float] = mapped_column(default=0.0)
    drift_score: Mapped[float] = mapped_column(default=0.0)  # alignment drift metric
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)


