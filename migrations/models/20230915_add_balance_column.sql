-- upgrade --

ALTER TABLE "player" ADD COLUMN "balance" BIGINT DEFAULT 0;
COMMENT ON COLUMN "player"."balance" IS 'Current balance';
UPDATE "player" SET "balance" = 0;