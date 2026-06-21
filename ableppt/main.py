"""
FastAPI 主服务
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List, Dict
import traceback

from ableppt.config import settings
from ableppt.models.job import Job
from ableppt.engine import PptEngine

# 创建应用
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="基于 Python 的 PPT 自动化生成服务",
)

# 创建渲染引擎
engine = PptEngine()


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
    }


@app.get(f"{settings.api_prefix}/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get(f"{settings.api_prefix}/templates")
async def list_templates():
    """列出可用模板"""
    templates = []

    if settings.templates_dir.exists():
        for template_file in settings.templates_dir.glob("*.pptx"):
            if not template_file.name.startswith("~"):  # 排除临时文件
                templates.append(
                    {
                        "name": template_file.stem,
                        "filename": template_file.name,
                        "path": str(template_file.relative_to(settings.base_dir)),
                        "size": template_file.stat().st_size,
                    }
                )

    return {"templates": templates, "count": len(templates)}


@app.post(f"{settings.api_prefix}/render")
async def render_ppt(job: Job):
    """
    渲染 PPT

    Args:
        job: 任务配置

    Returns:
        生成的 PPT 文件
    """
    try:
        # 渲染 PPT
        output_path = engine.render(job)

        # 返回文件
        return FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=output_path.name,
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if settings.debug:
            traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"渲染失败: {str(e)}")


@app.post(f"{settings.api_prefix}/render/async")
async def render_ppt_async(job: Job, background_tasks: BackgroundTasks):
    """
    异步渲染 PPT（后台任务）

    Args:
        job: 任务配置
        background_tasks: 后台任务

    Returns:
        任务ID和状态
    """
    import uuid

    task_id = str(uuid.uuid4())

    def render_task():
        """后台渲染任务"""
        try:
            engine.render(job)
        except Exception as e:
            print(f"渲染任务失败 [{task_id}]: {e}")
            if settings.debug:
                traceback.print_exc()

    background_tasks.add_task(render_task)

    return {
        "task_id": task_id,
        "status": "queued",
        "message": "渲染任务已加入队列",
    }


@app.get(f"{settings.api_prefix}/outputs")
async def list_outputs():
    """列出已生成的 PPT 文件"""
    outputs = []

    if settings.output_dir.exists():
        for output_file in settings.output_dir.glob("*.pptx"):
            if not output_file.name.startswith("~"):
                stat = output_file.stat()
                outputs.append(
                    {
                        "filename": output_file.name,
                        "path": str(output_file.relative_to(settings.base_dir)),
                        "size": stat.st_size,
                        "created": stat.st_ctime,
                        "modified": stat.st_mtime,
                    }
                )

    # 按修改时间降序排序
    outputs.sort(key=lambda x: x["modified"], reverse=True)

    return {"outputs": outputs, "count": len(outputs)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

