# Python 算法与学习笔记

> 一份面向**测试开发工程师（SDET）**的系统化学习与面试备战知识库，覆盖 Python 进阶、数据结构与算法、计算机网络、并发编程、自动化测试、数据库及主流工程工具。

笔记风格统一：**先讲"为什么"，再讲"是什么"**——用生活类比引入概念，从暴力解法推导到最优解法，强调设计意图而非死记硬背。

---

## 📚 内容总览

### 1. 数据结构与算法 (`algorithms/`)

按章节系统讲解算法基础，从抽象思维到核心数据结构与算法范式。

- `ch01_introduction.md`：引言与抽象思维
- `ch02`~`ch07_enhanced.md`：各章节增强版讲解
- `Python数据结构与算法知识图谱_claude.md`：完整知识图谱（约 12 种数据结构 + 10 种算法范式）
- `python算法与数据结构知识图谱_codex.md`：知识图谱补充版

### 2. LeetCode Hot 100 (`leetcode_hot100/`)

按题型分类，每题包含**核心考点 → 新手讲解 → 暴力到优化推导 → 代码实现**。

哈希、双指针、滑动窗口、子串、数组、矩阵、链表、二叉树、图论、回溯、二分查找、栈、堆、贪心、动态规划、多维动态规划、技巧。

### 3. Python 进阶 (`basic_python/`)

《流畅的 Python（第 2 版）》全 24 章学习笔记，涵盖数据模型、序列、字典集合、一等函数、装饰器闭包、面向对象、类型提示、并发模型、异步编程、元编程等。

### 4. 计算机网络 (`basic_network/`)

面向测试开发的网络知识路线（4 阶段渐进）：

- 学习路线概览 → 网络框架 → 核心协议（HTTP/TCP）→ 实战技巧 → 面试准备

### 5. 并发与测试 (根目录)

- `python_concurrency_complete.md`：asyncio / threading / GIL / 性能测试方法论
- `pytest_study_notes.md`：从"会写脚本"到"会设计框架"的接口自动化进阶

### 6. 数据库与工程工具 (根目录)

- `database_notes.md`：SQL、索引优化、Redis、MongoDB、测试隔离
- `redis_notes.md`：Redis 学习笔记
- `django_complete.md`：Django 完整笔记
- `docker_notes.md` / `k8s_notes.md`：容器与编排
- `linux_notes_optimized.md` / `shell_notes.md`：Linux 与 Shell

### 7. 参考书籍

- 《流畅的 Python（第 2 版）》PDF（Luciano Ramalho）

---

## 🎯 适用人群

- 准备**测试开发 / SDET** 岗位面试者
- 系统巩固 Python 进阶与算法基础的学习者
- 非科班出身、希望循序渐进建立技术深度的开发者

## 🗂️ 学习建议

| 目标 | 推荐路径 |
|------|----------|
| 算法刷题 | `leetcode_hot100/` + `algorithms/` 知识图谱 |
| Python 深入 | `basic_python/`（结合 PDF 原书） |
| 面试网络题 | `basic_network/05-interview-prep.md` |
| 自动化框架 | `pytest_study_notes.md` |
| 并发性能 | `python_concurrency_complete.md` |

---

## 📝 说明

笔记多以中文编写，内容随学习进度持续更新。文档为个人学习整理，供参考交流。
