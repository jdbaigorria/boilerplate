"""
Subscription and Plan models for SaaS billing.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum."""

    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class BillingInterval(str, enum.Enum):
    """Billing interval enum."""

    MONTHLY = "monthly"
    YEARLY = "yearly"


class Plan(Base):
    """
    Subscription plan model.
    Defines available subscription tiers with features and limits.
    """

    __tablename__ = "plans"

    # Basic information
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=False, default=0)
    price_yearly = Column(Numeric(10, 2), nullable=False, default=0)

    # Stripe integration (optional)
    stripe_price_id_monthly = Column(String(255), nullable=True)
    stripe_price_id_yearly = Column(String(255), nullable=True)
    stripe_product_id = Column(String(255), nullable=True)

    # Features (stored as JSON array)
    # Example: ["feature1", "feature2", "advanced_analytics"]
    features = Column(JSON, default=[], nullable=False)

    # Limits (stored as JSON object)
    # Example: {"max_users": 10, "max_projects": 5, "api_calls_per_month": 10000}
    limits = Column(JSON, default={}, nullable=False)

    # Visibility
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)

    # Display order
    display_order = Column(Integer, default=0, nullable=False)

    # Relationships
    subscriptions: "list[Subscription]" = relationship(
        "Subscription",
        back_populates="plan"
    )

    def __repr__(self) -> str:
        """String representation of Plan."""
        return f"<Plan {self.name}>"

    def has_feature(self, feature: str) -> bool:
        """
        Check if plan includes a specific feature.

        Args:
            feature: Feature name

        Returns:
            True if plan has the feature
        """
        return feature in (self.features or [])

    def get_limit(self, limit_key: str) -> int | None:
        """
        Get a specific limit value.

        Args:
            limit_key: Limit key (e.g., "max_users")

        Returns:
            Limit value or None if not set
        """
        return (self.limits or {}).get(limit_key)


class Subscription(Base):
    """
    Subscription model linking organizations to plans.
    Tracks billing and subscription status.
    """

    __tablename__ = "subscriptions"

    # Organization link
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One subscription per organization
        index=True
    )

    # Plan link
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Status
    status = Column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
        index=True
    )

    # Billing
    billing_interval = Column(
        Enum(BillingInterval),
        default=BillingInterval.MONTHLY,
        nullable=False
    )

    # Current billing period
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)

    # Trial
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime, nullable=True)

    # Stripe integration (optional)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_customer_id = Column(String(255), nullable=True, index=True)

    # Usage tracking (optional)
    usage_data = Column(JSON, default={}, nullable=False)

    # Relationships
    organization: "Organization" = relationship(
        "Organization",
        back_populates="subscription"
    )

    plan: "Plan" = relationship("Plan", back_populates="subscriptions")

    def __repr__(self) -> str:
        """String representation of Subscription."""
        return f"<Subscription org={self.organization_id} plan={self.plan_id} status={self.status}>"

    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    @property
    def is_trialing(self) -> bool:
        """Check if subscription is in trial period."""
        if self.status != SubscriptionStatus.TRIALING:
            return False

        if self.trial_end:
            return datetime.utcnow() < self.trial_end

        return False

    @property
    def days_until_renewal(self) -> int | None:
        """Calculate days until next renewal."""
        if not self.current_period_end:
            return None

        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)

    def has_feature_access(self, feature: str) -> bool:
        """
        Check if subscription has access to a feature.

        Args:
            feature: Feature name

        Returns:
            True if subscription's plan includes the feature
        """
        if not self.is_active:
            return False

        return self.plan.has_feature(feature) if self.plan else False

    def check_limit(self, limit_key: str, current_usage: int) -> bool:
        """
        Check if current usage is within plan limits.

        Args:
            limit_key: Limit key (e.g., "max_users")
            current_usage: Current usage value

        Returns:
            True if within limits, False if limit exceeded
        """
        if not self.is_active:
            return False

        limit = self.plan.get_limit(limit_key) if self.plan else None

        # No limit means unlimited
        if limit is None:
            return True

        return current_usage < limit

    def update_usage(self, key: str, value: int) -> None:
        """
        Update usage data.

        Args:
            key: Usage key
            value: Usage value
        """
        if not self.usage_data:
            self.usage_data = {}

        self.usage_data[key] = value
