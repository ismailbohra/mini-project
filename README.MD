alembic revision --autogenerate -m "add_deleted_status_to_report_enum"

alembic upgrade head  

-- INSERT INTO public.posts (author_id, title, description, image_path,is_deleted)  -- exclude id
-- SELECT author_id, title, description, image_path, False
-- FROM public.posts;
SELECT * FROM public.posts
ORDER BY id ASC 