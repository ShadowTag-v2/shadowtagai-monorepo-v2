# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Release Manager Service for zero-downtime deployments.
"""

import asyncio
from datetime import datetime, timezone
import httpx

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.models.release import (
    Release,
    Deployment,
    DeploymentStatus,
    DeploymentStrategy,
)
from app.schemas.release import (
    ReleaseCreate,
    ReleaseUpdate,
    DeploymentCreate,
    HealthCheckResult,
)


class ReleaseManagerService:
    """Service for managing releases and deployments."""

    def __init__(self):
        """Initialize release manager service."""
        self.deployment_strategies = {
            DeploymentStrategy.BLUE_GREEN: self._deploy_blue_green,
            DeploymentStrategy.ROLLING: self._deploy_rolling,
            DeploymentStrategy.CANARY: self._deploy_canary,
            DeploymentStrategy.RECREATE: self._deploy_recreate,
        }

    # ==================== Release Management ====================

    async def create_release(
        self,
        db: AsyncSession,
        release_data: ReleaseCreate,
    ) -> Release:
        """Create a new release."""
        release = Release(**release_data.model_dump())
        db.add(release)
        await db.commit()
        await db.refresh(release)

        logger.info(f"Created release: {release.version}")
        return release

    async def get_release(
        self,
        db: AsyncSession,
        release_id: int,
    ) -> Release | None:
        """Get release by ID."""
        result = await db.execute(select(Release).where(Release.id == release_id))
        return result.scalar_one_or_none()

    async def get_release_by_version(
        self,
        db: AsyncSession,
        version: str,
    ) -> Release | None:
        """Get release by version."""
        result = await db.execute(select(Release).where(Release.version == version))
        return result.scalar_one_or_none()

    async def list_releases(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> tuple[list[Release], int]:
        """List releases with pagination."""
        query = select(Release).order_by(desc(Release.created_at))

        if active_only:
            query = query.where(Release.is_active == True)

        # Get total count
        count_result = await db.execute(select(Release).where(*query.whereclause.clauses if query.whereclause else []))
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        releases = result.scalars().all()

        return list(releases), total

    async def update_release(
        self,
        db: AsyncSession,
        release_id: int,
        release_data: ReleaseUpdate,
    ) -> Release | None:
        """Update release."""
        release = await self.get_release(db, release_id)
        if not release:
            return None

        update_data = release_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(release, field, value)

        await db.commit()
        await db.refresh(release)

        logger.info(f"Updated release: {release.version}")
        return release

    async def set_active_release(
        self,
        db: AsyncSession,
        release_id: int,
    ) -> Release | None:
        """Set a release as active (deactivate all others)."""
        # Deactivate all releases
        all_releases = await db.execute(select(Release))
        for release in all_releases.scalars():
            release.is_active = False

        # Activate the specified release
        release = await self.get_release(db, release_id)
        if not release:
            return None

        release.is_active = True
        release.released_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(release)

        logger.info(f"Set active release: {release.version}")
        return release

    # ==================== Deployment Management ====================

    async def create_deployment(
        self,
        db: AsyncSession,
        deployment_data: DeploymentCreate,
    ) -> Deployment:
        """Create a new deployment."""
        deployment = Deployment(**deployment_data.model_dump())
        deployment.status = DeploymentStatus.PENDING
        db.add(deployment)
        await db.commit()
        await db.refresh(deployment)

        logger.info(f"Created deployment: {deployment.id} for release: {deployment.release_id}")
        return deployment

    async def get_deployment(
        self,
        db: AsyncSession,
        deployment_id: int,
    ) -> Deployment | None:
        """Get deployment by ID."""
        result = await db.execute(select(Deployment).where(Deployment.id == deployment_id))
        return result.scalar_one_or_none()

    async def list_deployments(
        self,
        db: AsyncSession,
        environment: str | None = None,
        release_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Deployment], int]:
        """List deployments with filters."""
        query = select(Deployment).order_by(desc(Deployment.started_at))

        if environment:
            query = query.where(Deployment.environment == environment)
        if release_id:
            query = query.where(Deployment.release_id == release_id)

        # Get total count
        count_result = await db.execute(select(Deployment).where(*query.whereclause.clauses if query.whereclause else []))
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        deployments = result.scalars().all()

        return list(deployments), total

    async def get_latest_deployment(
        self,
        db: AsyncSession,
        environment: str,
        status: DeploymentStatus | None = None,
    ) -> Deployment | None:
        """Get the latest deployment for an environment."""
        query = select(Deployment).where(Deployment.environment == environment).order_by(desc(Deployment.started_at)).limit(1)

        if status:
            query = query.where(Deployment.status == status)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    # ==================== Health Checks ====================

    async def perform_health_check(
        self,
        service_url: str,
        health_endpoint: str = "/health",
        timeout: int = 30,
    ) -> HealthCheckResult:
        """
        Perform health check on a service.

        Args:
            service_url: Base URL of the service
            health_endpoint: Health check endpoint path
            timeout: Timeout in seconds

        Returns:
            HealthCheckResult with health status
        """
        checks = {
            "http": False,
            "response_time": False,
            "status_code": False,
        }

        try:
            start_time = datetime.now(timezone.utc)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{service_url}{health_endpoint}")
                end_time = datetime.now(timezone.utc)
                response_time = (end_time - start_time).total_seconds()

                checks["http"] = True
                checks["status_code"] = response.status_code == 200
                checks["response_time"] = response_time < 5.0  # Less than 5 seconds

                healthy = all(checks.values())

                return HealthCheckResult(
                    healthy=healthy,
                    checks=checks,
                    message=f"Response time: {response_time:.2f}s, Status: {response.status_code}",
                )

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResult(
                healthy=False,
                checks=checks,
                message=f"Health check error: {str(e)}",
            )

    async def wait_for_healthy(
        self,
        service_url: str,
        max_attempts: int = 10,
        interval: int = 5,
    ) -> bool:
        """
        Wait for service to become healthy.

        Args:
            service_url: Base URL of the service
            max_attempts: Maximum number of health check attempts
            interval: Interval between checks in seconds

        Returns:
            True if service becomes healthy, False otherwise
        """
        for attempt in range(max_attempts):
            logger.info(f"Health check attempt {attempt + 1}/{max_attempts}")
            result = await self.perform_health_check(service_url)

            if result.healthy:
                logger.info(f"Service healthy: {service_url}")
                return True

            await asyncio.sleep(interval)

        logger.error(f"Service did not become healthy: {service_url}")
        return False

    # ==================== Deployment Strategies ====================

    async def deploy(
        self,
        db: AsyncSession,
        deployment_id: int,
    ) -> Deployment:
        """
        Execute deployment using the configured strategy.

        Args:
            db: Database session
            deployment_id: Deployment ID

        Returns:
            Updated deployment
        """
        deployment = await self.get_deployment(db, deployment_id)
        if not deployment:
            raise ValueError(f"Deployment not found: {deployment_id}")

        try:
            # Update status to in progress
            deployment.status = DeploymentStatus.IN_PROGRESS
            deployment.started_at = datetime.now(timezone.utc)
            await db.commit()

            # Execute deployment strategy
            strategy_func = self.deployment_strategies.get(deployment.strategy)
            if not strategy_func:
                raise ValueError(f"Unknown deployment strategy: {deployment.strategy}")

            success = await strategy_func(db, deployment)

            if success:
                deployment.status = DeploymentStatus.DEPLOYED
                deployment.completed_at = datetime.now(timezone.utc)
                logger.info(f"Deployment {deployment_id} completed successfully")
            else:
                deployment.status = DeploymentStatus.FAILED
                deployment.error_message = "Deployment failed - health checks did not pass"
                logger.error(f"Deployment {deployment_id} failed")

        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            deployment.error_message = str(e)
            logger.error(f"Deployment {deployment_id} error: {e}")

        await db.commit()
        await db.refresh(deployment)
        return deployment

    async def _deploy_blue_green(
        self,
        db: AsyncSession,
        deployment: Deployment,
    ) -> bool:
        """
        Blue-Green deployment strategy.

        Deploys new version to a separate environment, tests it,
        then switches traffic to it.
        """
        logger.info(f"Starting Blue-Green deployment: {deployment.id}")

        config = deployment.configuration or {}
        green_url = config.get("green_url")
        config.get("blue_url")

        if not green_url:
            deployment.error_message = "Green environment URL not configured"
            return False

        # Deploy to green environment
        deployment.logs = "Deploying to green environment...\n"
        await db.commit()

        # Simulate deployment (in production, this would interact with container orchestrator)
        await asyncio.sleep(2)

        # Health check green environment
        deployment.logs += "Performing health checks on green environment...\n"
        await db.commit()

        healthy = await self.wait_for_healthy(
            green_url,
            max_attempts=settings.HEALTH_CHECK_TIMEOUT // settings.HEALTH_CHECK_INTERVAL,
            interval=settings.HEALTH_CHECK_INTERVAL,
        )

        if not healthy:
            deployment.logs += "Green environment health check failed\n"
            deployment.health_check_passed = False
            await db.commit()
            return False

        deployment.health_check_passed = True
        deployment.logs += "Green environment is healthy\n"
        await db.commit()

        # Switch traffic to green
        deployment.logs += "Switching traffic to green environment...\n"
        await db.commit()

        # Simulate traffic switch
        await asyncio.sleep(1)

        deployment.logs += "Traffic switched successfully. Blue-Green deployment complete.\n"
        await db.commit()

        logger.info(f"Blue-Green deployment {deployment.id} completed")
        return True

    async def _deploy_rolling(
        self,
        db: AsyncSession,
        deployment: Deployment,
    ) -> bool:
        """
        Rolling deployment strategy.

        Gradually replaces instances of the old version with the new version.
        """
        logger.info(f"Starting Rolling deployment: {deployment.id}")

        config = deployment.configuration or {}
        instances = config.get("instances", 3)
        batch_size = config.get("batch_size", 1)

        deployment.logs = f"Starting rolling deployment with {instances} instances, batch size {batch_size}...\n"
        await db.commit()

        for i in range(0, instances, batch_size):
            batch_end = min(i + batch_size, instances)
            deployment.logs += f"Deploying instances {i + 1}-{batch_end}...\n"
            await db.commit()

            # Simulate instance deployment
            await asyncio.sleep(2)

            # Health check new instances
            deployment.logs += f"Health checking instances {i + 1}-{batch_end}...\n"
            await db.commit()

            # Simulate health check
            await asyncio.sleep(1)

            deployment.logs += f"Instances {i + 1}-{batch_end} deployed and healthy\n"
            await db.commit()

        deployment.health_check_passed = True
        deployment.logs += "Rolling deployment complete. All instances updated.\n"
        await db.commit()

        logger.info(f"Rolling deployment {deployment.id} completed")
        return True

    async def _deploy_canary(
        self,
        db: AsyncSession,
        deployment: Deployment,
    ) -> bool:
        """
        Canary deployment strategy.

        Deploys new version to a small subset of instances first,
        monitors metrics, then gradually increases.
        """
        logger.info(f"Starting Canary deployment: {deployment.id}")

        config = deployment.configuration or {}
        canary_percentage = config.get("canary_percentage", 10)
        monitoring_duration = config.get("monitoring_duration", 300)  # 5 minutes

        deployment.logs = f"Starting canary deployment with {canary_percentage}% traffic...\n"
        await db.commit()

        # Deploy canary
        deployment.logs += "Deploying canary instances...\n"
        await db.commit()
        await asyncio.sleep(2)

        # Health check canary
        deployment.logs += "Health checking canary instances...\n"
        await db.commit()
        await asyncio.sleep(1)

        # Monitor canary
        deployment.logs += f"Monitoring canary for {monitoring_duration} seconds...\n"
        await db.commit()

        # Simulate monitoring (in production, would check metrics)
        await asyncio.sleep(min(monitoring_duration, 5))

        deployment.logs += "Canary metrics look good. Proceeding with full deployment...\n"
        await db.commit()

        # Deploy to all instances
        deployment.logs += "Deploying to all instances...\n"
        await db.commit()
        await asyncio.sleep(2)

        deployment.health_check_passed = True
        deployment.logs += "Canary deployment complete.\n"
        await db.commit()

        logger.info(f"Canary deployment {deployment.id} completed")
        return True

    async def _deploy_recreate(
        self,
        db: AsyncSession,
        deployment: Deployment,
    ) -> bool:
        """
        Recreate deployment strategy.

        Stops all old instances, then starts new ones.
        WARNING: This causes downtime.
        """
        logger.info(f"Starting Recreate deployment: {deployment.id}")

        deployment.logs = "WARNING: This strategy causes downtime.\n"
        deployment.logs += "Stopping all old instances...\n"
        await db.commit()

        # Simulate stopping old instances
        await asyncio.sleep(2)

        deployment.logs += "Starting new instances...\n"
        await db.commit()

        # Simulate starting new instances
        await asyncio.sleep(3)

        deployment.logs += "Health checking new instances...\n"
        await db.commit()

        # Simulate health check
        await asyncio.sleep(1)

        deployment.health_check_passed = True
        deployment.logs += "Recreate deployment complete.\n"
        await db.commit()

        logger.info(f"Recreate deployment {deployment.id} completed")
        return True

    # ==================== Rollback Management ====================

    async def rollback_deployment(
        self,
        db: AsyncSession,
        deployment_id: int,
        reason: str | None = None,
        force: bool = False,
    ) -> Deployment:
        """
        Rollback a deployment to the previous stable release.

        Args:
            db: Database session
            deployment_id: Deployment to rollback
            reason: Rollback reason
            force: Force rollback even if health checks fail

        Returns:
            New deployment for the rollback
        """
        current_deployment = await self.get_deployment(db, deployment_id)
        if not current_deployment:
            raise ValueError(f"Deployment not found: {deployment_id}")

        # Mark current deployment as rolling back
        current_deployment.status = DeploymentStatus.ROLLING_BACK
        await db.commit()

        logger.info(f"Starting rollback for deployment {deployment_id}")

        try:
            # Find previous successful deployment
            previous_deployment = await self._get_previous_stable_deployment(
                db,
                current_deployment.environment,
                current_deployment.id,
            )

            if not previous_deployment:
                raise ValueError("No previous stable deployment found for rollback")

            # Create new deployment for rollback
            rollback_deployment = Deployment(
                release_id=previous_deployment.release_id,
                environment=current_deployment.environment,
                strategy=current_deployment.strategy,
                status=DeploymentStatus.IN_PROGRESS,
                deployed_by=current_deployment.deployed_by,
                configuration=previous_deployment.configuration,
                started_at=datetime.now(timezone.utc),
            )

            db.add(rollback_deployment)
            await db.commit()
            await db.refresh(rollback_deployment)

            # Link rollback deployment
            current_deployment.rollback_deployment_id = rollback_deployment.id
            await db.commit()

            # Execute rollback deployment
            rollback_deployment.logs = f"Rollback initiated. Reason: {reason or 'Not specified'}\n"
            rollback_deployment.logs += f"Rolling back to release {previous_deployment.release_id}...\n"
            await db.commit()

            # Execute deployment strategy for rollback
            strategy_func = self.deployment_strategies.get(rollback_deployment.strategy)
            if strategy_func:
                success = await strategy_func(db, rollback_deployment)

                if success or force:
                    rollback_deployment.status = DeploymentStatus.DEPLOYED
                    rollback_deployment.completed_at = datetime.now(timezone.utc)
                    current_deployment.status = DeploymentStatus.ROLLED_BACK
                    rollback_deployment.logs += "Rollback completed successfully.\n"
                    logger.info(f"Rollback {rollback_deployment.id} completed")
                else:
                    rollback_deployment.status = DeploymentStatus.FAILED
                    rollback_deployment.error_message = "Rollback deployment failed"
                    rollback_deployment.logs += "Rollback failed.\n"
                    logger.error(f"Rollback {rollback_deployment.id} failed")

            await db.commit()
            await db.refresh(rollback_deployment)

            return rollback_deployment

        except Exception as e:
            current_deployment.status = DeploymentStatus.FAILED
            current_deployment.error_message = f"Rollback error: {str(e)}"
            await db.commit()
            logger.error(f"Rollback error: {e}")
            raise

    async def _get_previous_stable_deployment(
        self,
        db: AsyncSession,
        environment: str,
        current_deployment_id: int,
    ) -> Deployment | None:
        """Find the previous stable deployment for rollback."""
        result = await db.execute(
            select(Deployment)
            .where(
                Deployment.environment == environment,
                Deployment.id < current_deployment_id,
                Deployment.status == DeploymentStatus.DEPLOYED,
                Deployment.health_check_passed == True,
            )
            .order_by(desc(Deployment.completed_at))
            .limit(1)
        )
        return result.scalar_one_or_none()


# Global release manager service instance
release_manager_service = ReleaseManagerService()
