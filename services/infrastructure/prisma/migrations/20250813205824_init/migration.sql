-- CreateTable
CREATE TABLE "Session" (
    "id" TEXT NOT NULL,
    "app_name" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "session_id" TEXT NOT NULL,
    "state" JSONB,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "expires_at" TIMESTAMP(3),

    CONSTRAINT "Session_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Execution" (
    "id" TEXT NOT NULL,
    "session_id" TEXT NOT NULL,
    "agent_name" TEXT NOT NULL,
    "agent_type" TEXT NOT NULL,
    "workflow_name" TEXT,
    "input_data" JSONB NOT NULL,
    "output_data" JSONB,
    "status" TEXT NOT NULL,
    "error_message" TEXT,
    "started_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(3),
    "duration_ms" INTEGER,
    "token_usage" JSONB,

    CONSTRAINT "Execution_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Result" (
    "id" TEXT NOT NULL,
    "execution_id" TEXT NOT NULL,
    "result_type" TEXT NOT NULL,
    "data" JSONB NOT NULL,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Result_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AuditLog" (
    "id" TEXT NOT NULL,
    "session_id" TEXT,
    "execution_id" TEXT,
    "user_id" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "resource" TEXT NOT NULL,
    "details" JSONB,
    "ip_address" TEXT,
    "user_agent" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AuditLog_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ToolRegistry" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "version" TEXT NOT NULL,
    "description" TEXT,
    "specification" JSONB NOT NULL,
    "function_def" TEXT,
    "categories" TEXT[],
    "dependencies" TEXT[],
    "active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ToolRegistry_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ConfigurationVersion" (
    "id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "version" TEXT NOT NULL,
    "checksum" TEXT NOT NULL,
    "specification" JSONB NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "created_by" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ConfigurationVersion_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Session_session_id_key" ON "Session"("session_id");

-- CreateIndex
CREATE INDEX "Session_user_id_idx" ON "Session"("user_id");

-- CreateIndex
CREATE INDEX "Session_app_name_idx" ON "Session"("app_name");

-- CreateIndex
CREATE INDEX "Session_created_at_idx" ON "Session"("created_at");

-- CreateIndex
CREATE INDEX "Execution_session_id_idx" ON "Execution"("session_id");

-- CreateIndex
CREATE INDEX "Execution_agent_name_idx" ON "Execution"("agent_name");

-- CreateIndex
CREATE INDEX "Execution_status_idx" ON "Execution"("status");

-- CreateIndex
CREATE INDEX "Execution_started_at_idx" ON "Execution"("started_at");

-- CreateIndex
CREATE INDEX "Result_execution_id_idx" ON "Result"("execution_id");

-- CreateIndex
CREATE INDEX "Result_result_type_idx" ON "Result"("result_type");

-- CreateIndex
CREATE INDEX "AuditLog_user_id_idx" ON "AuditLog"("user_id");

-- CreateIndex
CREATE INDEX "AuditLog_action_idx" ON "AuditLog"("action");

-- CreateIndex
CREATE INDEX "AuditLog_created_at_idx" ON "AuditLog"("created_at");

-- CreateIndex
CREATE UNIQUE INDEX "ToolRegistry_name_key" ON "ToolRegistry"("name");

-- CreateIndex
CREATE INDEX "ToolRegistry_name_idx" ON "ToolRegistry"("name");

-- CreateIndex
CREATE INDEX "ToolRegistry_categories_idx" ON "ToolRegistry"("categories");

-- CreateIndex
CREATE INDEX "ToolRegistry_active_idx" ON "ToolRegistry"("active");

-- CreateIndex
CREATE INDEX "ConfigurationVersion_type_idx" ON "ConfigurationVersion"("type");

-- CreateIndex
CREATE INDEX "ConfigurationVersion_name_idx" ON "ConfigurationVersion"("name");

-- CreateIndex
CREATE INDEX "ConfigurationVersion_active_idx" ON "ConfigurationVersion"("active");

-- CreateIndex
CREATE INDEX "ConfigurationVersion_checksum_idx" ON "ConfigurationVersion"("checksum");

-- CreateIndex
CREATE UNIQUE INDEX "ConfigurationVersion_type_name_version_key" ON "ConfigurationVersion"("type", "name", "version");

-- AddForeignKey
ALTER TABLE "Execution" ADD CONSTRAINT "Execution_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "Session"("session_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Result" ADD CONSTRAINT "Result_execution_id_fkey" FOREIGN KEY ("execution_id") REFERENCES "Execution"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AuditLog" ADD CONSTRAINT "AuditLog_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "Session"("session_id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AuditLog" ADD CONSTRAINT "AuditLog_execution_id_fkey" FOREIGN KEY ("execution_id") REFERENCES "Execution"("id") ON DELETE SET NULL ON UPDATE CASCADE;
