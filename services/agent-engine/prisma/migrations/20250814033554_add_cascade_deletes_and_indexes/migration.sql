/*
  Warnings:

  - You are about to drop the column `checksum` on the `ConfigurationVersion` table. All the data in the column will be lost.

*/
-- DropForeignKey
ALTER TABLE "agent_engine"."AuditLog" DROP CONSTRAINT "AuditLog_execution_id_fkey";

-- DropForeignKey
ALTER TABLE "agent_engine"."AuditLog" DROP CONSTRAINT "AuditLog_session_id_fkey";

-- DropForeignKey
ALTER TABLE "agent_engine"."Execution" DROP CONSTRAINT "Execution_session_id_fkey";

-- DropForeignKey
ALTER TABLE "agent_engine"."Result" DROP CONSTRAINT "Result_execution_id_fkey";

-- DropIndex
DROP INDEX "agent_engine"."ConfigurationVersion_checksum_idx";

-- AlterTable
ALTER TABLE "agent_engine"."ConfigurationVersion" DROP COLUMN "checksum";

-- AlterTable
ALTER TABLE "agent_engine"."Session" ADD COLUMN     "backend" TEXT NOT NULL DEFAULT 'memory';

-- CreateIndex
CREATE INDEX "Execution_session_id_status_idx" ON "agent_engine"."Execution"("session_id", "status");

-- CreateIndex
CREATE INDEX "Execution_agent_name_started_at_idx" ON "agent_engine"."Execution"("agent_name", "started_at");

-- CreateIndex
CREATE INDEX "Session_backend_idx" ON "agent_engine"."Session"("backend");

-- CreateIndex
CREATE INDEX "Session_user_id_app_name_idx" ON "agent_engine"."Session"("user_id", "app_name");

-- CreateIndex
CREATE INDEX "Session_backend_created_at_idx" ON "agent_engine"."Session"("backend", "created_at");

-- AddForeignKey
ALTER TABLE "agent_engine"."Execution" ADD CONSTRAINT "Execution_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "agent_engine"."Session"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "agent_engine"."Result" ADD CONSTRAINT "Result_execution_id_fkey" FOREIGN KEY ("execution_id") REFERENCES "agent_engine"."Execution"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "agent_engine"."AuditLog" ADD CONSTRAINT "AuditLog_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "agent_engine"."Session"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "agent_engine"."AuditLog" ADD CONSTRAINT "AuditLog_execution_id_fkey" FOREIGN KEY ("execution_id") REFERENCES "agent_engine"."Execution"("id") ON DELETE CASCADE ON UPDATE CASCADE;
