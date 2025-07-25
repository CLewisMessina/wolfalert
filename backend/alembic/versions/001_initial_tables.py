"""Initial tables creation

Revision ID: 001_initial
Revises: 
Create Date: 2025-07-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_profiles table
    op.create_table('user_profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('profile_name', sa.String(length=100), nullable=False),
    sa.Column('industry', sa.String(length=50), nullable=False),
    sa.Column('department', sa.String(length=50), nullable=False),
    sa.Column('role_level', sa.String(length=30), nullable=False),
    sa.Column('user_session_id', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)

    # Create articles table
    op.create_table('articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('source_name', sa.String(length=100), nullable=False),
    sa.Column('source_reliability', sa.String(length=20), nullable=False),
    sa.Column('published_at', sa.DateTime(), nullable=False),
    sa.Column('fetched_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('is_processed', sa.Boolean(), nullable=True),
    sa.Column('processing_attempts', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url')
    )
    op.create_index('idx_article_expires', 'articles', ['expires_at'], unique=False)
    op.create_index('idx_article_processed', 'articles', ['is_processed'], unique=False)
    op.create_index('idx_article_published', 'articles', ['published_at'], unique=False)
    op.create_index(op.f('ix_articles_id'), 'articles', ['id'], unique=False)
    op.create_index(op.f('ix_articles_url'), 'articles', ['url'], unique=False)

    # Create rss_sources table
    op.create_table('rss_sources',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.Column('source_type', sa.String(length=30), nullable=False),
    sa.Column('reliability', sa.String(length=20), nullable=False),
    sa.Column('company', sa.String(length=100), nullable=True),
    sa.Column('industries', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('weight', sa.Numeric(precision=3, scale=2), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('last_fetched', sa.DateTime(), nullable=True),
    sa.Column('fetch_frequency_hours', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('url')
    )
    op.create_index('idx_source_active', 'rss_sources', ['is_active'], unique=False)
    op.create_index('idx_source_fetch', 'rss_sources', ['last_fetched'], unique=False)
    op.create_index(op.f('ix_rss_sources_id'), 'rss_sources', ['id'], unique=False)

    # Create article_insights table
    op.create_table('article_insights',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('profile_hash', sa.String(length=64), nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('impact_reasoning', sa.Text(), nullable=False),
    sa.Column('impact_type', sa.String(length=20), nullable=False),
    sa.Column('impact_score', sa.Numeric(precision=3, scale=2), nullable=False),
    sa.Column('processing_time_ms', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_article_profile', 'article_insights', ['article_id', 'profile_hash'], unique=False)
    op.create_index('idx_profile_score', 'article_insights', ['profile_hash', 'impact_score'], unique=False)
    op.create_index(op.f('ix_article_insights_id'), 'article_insights', ['id'], unique=False)

    # Create reports table
    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('generated_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['user_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_profile_reports', 'reports', ['profile_id', 'generated_at'], unique=False)
    op.create_index('idx_report_expires', 'reports', ['expires_at'], unique=False)
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)

    # Create user_interactions table
    op.create_table('user_interactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=20), nullable=False),
    sa.Column('interaction_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.ForeignKeyConstraint(['profile_id'], ['user_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_article_interactions', 'user_interactions', ['article_id', 'action'], unique=False)
    op.create_index('idx_profile_interactions', 'user_interactions', ['profile_id', 'interaction_time'], unique=False)
    op.create_index(op.f('ix_user_interactions_id'), 'user_interactions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('user_interactions')
    op.drop_table('reports')
    op.drop_table('article_insights')
    op.drop_table('rss_sources')
    op.drop_table('articles')
    op.drop_table('user_profiles')