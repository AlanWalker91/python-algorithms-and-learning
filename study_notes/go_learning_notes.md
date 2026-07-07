# Go 语言学习笔记（面向测试开发面试）

> 面向有Python基础的学习者。重点讲「与 Python 不同地方。
---

## 目录

- [第一阶段：语法基础](#第一阶段语法基础)
  - [1. 变量、类型与零值](#1-变量类型与零值)
  - [2. 函数与多返回值、error](#2-函数与多返回值error)
  - [3. slice（切片）](#3-slice切片)
  - [4. map](#4-map)
  - [5. struct 与方法、接收者](#5-struct-与方法接收者)
- [第二阶段：Go 的灵魂](#第二阶段go-的灵魂)
  - [6. 接口 interface](#6-接口-interface)
  - [7. 类型断言与 type switch](#7-类型断言与-type-switch)
- [第三阶段：并发](#第三阶段并发)
  - [8. goroutine](#8-goroutine)
  - [9. channel](#9-channel)
  - [10. select](#10-select)
  - [11. sync.Mutex 与并发 bug](#11-syncmutex-与并发-bug)
- [第四阶段：工程与测试](#第四阶段工程与测试)
  - [12. go test 与表驱动测试](#12-go-test-与表驱动测试)
- [高频测开面试题速查](#高频测开面试题速查)

---

# 第一阶段：语法基础

## 1. 变量、类型与零值

### 核心概念

Go 是**静态类型**语言：类型在**编译期**就钉死在变量上，且**终身不变**。这与 Python「变量只是贴在对象上的名字标签、类型跟着值走」完全相反。

`:=` 是短变量声明，一次做两件事：
1. **声明**——创建新变量并**永久绑定一个类型**（由右侧值推导）。
2. **赋值**——把右侧值放进去。

### 代码示例

```go
package main

import "fmt"

func main() {
    x := 5          // 推导为 int，类型从此定死
    // x = "hello"  // 编译错误：不能把 string 赋给 int 变量

    var name string = "Go"  // 完整声明写法：var 变量名 类型 = 值
    age := 25               // 简写，推导为 int
    pi := 3.14              // 推导为 float64

    // 零值：声明但未赋值时的默认值，不是 null/None，且可直接用
    var n int       // 0
    var s string    // ""（空字符串）
    var b bool      // false
    var p *int      // nil（指针、slice、map、channel、interface 的零值都是 nil）

    fmt.Println(x, name, age, pi, n, s, b, p)

    // 无隐式类型转换：不同数值类型不能直接运算
    a := 5
    c := 3.0
    // sum := a + c          // 编译错误：int + float64 不允许
    sum := float64(a) + c    // 必须显式转换
    fmt.Println(sum)         // 8
}
```

### 执行逻辑

- `x := 5`：编译器看到右侧是整数字面量，把 `x` 定为 `int`（64 位机器上是 64 位）。之后任何非 int 赋值都在**编译期**被拒绝——错误在运行前就暴露。
- 零值机制：`var n int` 后 `n` 立刻是可用的 `0`，不存在「未初始化」的未定义状态。这消除了 Python 里访问未赋值变量的 `NameError`，也是 Go 代码里很少见到 `if x is None` 防御性检查的原因。

### 常见陷阱

- ⚠️ **误以为会隐式转换**：`int + float64` 在 Go 里直接编译不过。Python 里 `5 + 3.0` 会悄悄提升，Go 拒绝这种「偷偷转换」。
- ⚠️ **bool 零值是 `false` 不是 `true`**：所有零值统一含义是「空 / 无 / 尚未设置」——`0`、`""`、`false`、`nil`。
- ⚠️ `:=` 只能在函数内部用；包级变量必须用 `var`。

---

## 2. 函数与多返回值、error

### 核心概念

Go 函数最有辨识度的特性是**多返回值**。类型写在名字**后面**（与 Python 相反）。最经典的多返回模式是 `(结果, error)`——Go 用它替代 Python 的 `try/except`：**错误是普通返回值，不是异常**。

### 代码示例

```go
package main

import (
    "errors"
    "fmt"
)

// func 函数名(参数 类型) (返回类型列表)
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("除数不能为零")  // 失败：返回零值 + 错误
    }
    return a / b, nil                        // 成功：返回结果 + nil（表示无错误）
}

func main() {
    // 铁律：拿到 (值, err)，永远先检查 err，再用值
    result, err := divide(10, 2)
    if err != nil {
        fmt.Println("出错:", err)
        return
    }
    fmt.Println("结果:", result)  // 5

    // 错误路径演示
    result2, err2 := divide(10, 0)
    if err2 != nil {
        fmt.Println("出错:", err2)  // 出错: 除数不能为零
        return
    }
    fmt.Println(result2)  // 不会执行到这里
}
```

### 执行逻辑与数据流向

- `divide(10, 0)`：`b == 0` 成立，走 `return 0, errors.New(...)`。返回值 `result2 = 0`、`err2 =` 错误对象。
- 这里的 `0` 是**占位零值**，不是「10 除以 0 等于 0」的真实结果。所以必须先 `if err != nil` 确认没出错，才能信任 `result`。
- Go 代码里满屏 `if err != nil`：错误沿返回值链条**手动向上传递**，没有异常在背后偷偷飞。看代码就知道哪里可能出错。

### 常见陷阱

- ⚠️ **先用值再检查 err**（顺序反了）：出错时值是无意义的零值，直接使用会把假数据往下传，且**不会崩溃**（不像 Python 抛异常），bug 极隐蔽。正确顺序永远是「先 `if err != nil`，再碰值」。
- ⚠️ 忽略 error（用 `_` 丢弃）：`result, _ := divide(...)` 语法合法但危险，等于放弃了错误处理。

---

## 3. slice（切片）

### 核心概念

slice 是 Go 版的动态数组（对应 Python 的 `list`），但**面试重灾区**全在它的底层机制。

**slice 本身不存数据**，它是一个「三件套」头结构，指向底层一个真正存数据的数组：

```
slice = { 指针 → 底层数组,  长度 len,  容量 cap }
```

- **指针**：指向底层数组的起点
- **len**：当前元素个数
- **cap**：底层数组总容量（不扩容时能放的最大数）

**数组 vs slice**：数组 `[3]int` 长度是类型的一部分、固定、值传递会整个拷贝；slice `[]int` 是对底层数组的**引用视图**，长度可变，传递时只拷贝三件套、**共享底层数组**。

### 代码示例

```go
package main

import "fmt"

func main() {
    // 创建
    nums := []int{1, 2, 3}
    nums = append(nums, 4)       // append 必须把结果赋值回去（见执行逻辑）
    fmt.Println(nums, len(nums), cap(nums))  // [1 2 3 4] 4 ...

    // make 预分配：make([]T, len, cap)
    buf := make([]int, 0, 10)    // len=0, cap=10，追加前 10 个不扩容
    _ = buf

    // 共享底层数组的坑
    a := []int{1, 2, 3, 4, 5}
    b := a[0:2]                  // b: len=2, cap=5，与 a 共享底层数组
    b = append(b, 99)           // len(2) < cap(5)，未满 → 就地写入索引 2
    fmt.Println(a)              // [1 2 99 4 5]  ← a 被改了！
    fmt.Println(b)              // [1 2 99]

    // 用三索引切片保护原 slice
    c := a[0:2:2]               // a[low:high:max]，cap 被限制为 2
    c = append(c, 88)          // 已满 → 分配新数组，不影响 a
    fmt.Println(a)             // 不受 c 的 append 影响
}
```

### 执行逻辑与数据流向

- **为什么 `nums = append(nums, x)` 必须赋值回去**：当 `len == cap`（底层数组满了），append 无法原地追加，会 ①申请更大的新数组 ②拷贝旧数据 ③追加新元素 ④返回**指向新数组的新三件套**。旧三件套仍指向老数组，所以必须接住返回值。
- **共享底层数组的踩踏**：`b := a[0:2]` 让 b 与 a 指向同一底层数组，且 b 的 `cap=5`（还有空位）。`append(b, 99)` 发现未满，直接把 99 写进底层数组索引 2——那正是 `a[2]`，于是原来的 `3` 被覆盖。
- **扩容策略**：容量小时**翻倍**，超过约 1024 后按约 **1.25 倍**增长（具体倍数随 Go 版本微调）。扩容后新 slice 与原底层数组**脱钩**。

### 常见陷阱

- ⚠️ **函数参数是 slice，函数内 append 偷偷改了调用方数据**——且时灵时不灵，取决于当时 `len < cap` 有没有剩余空位。经典面试陷阱。防御手段：三索引切片 `s[low:high:max]` 限制 cap，或对结果用 `copy` 拷贝一份。
- ⚠️ `b := a` 这种直接赋值也共享底层数组，`b[0]=99` 会改到 `a[0]`（这点 Python list 行为一致，不算坑）。真正的坑是 **共享 + append** 组合。

---

## 4. map

### 核心概念

map 是 Go 版的哈希表（对应 Python 的 `dict`）。类型写作 `map[键类型]值类型`。三个必知特性：查不存在的键返回**值类型的零值**、用 **comma-ok** 区分「不存在 vs 零值」、**遍历顺序随机**。

### 代码示例

```go
package main

import (
    "fmt"
    "sort"
)

func main() {
    m := map[string]int{"a": 1, "b": 2}
    m["c"] = 3                    // 新增/修改
    delete(m, "a")               // 删除键

    // 查不存在的键：返回值类型（int）的零值 0，不 panic
    v := m["不存在"]
    fmt.Println(v)               // 0

    // comma-ok：区分「键不存在」与「键存在但值为 0」
    val, ok := m["b"]
    if ok {
        fmt.Println("存在, 值为", val)   // 存在, 值为 2
    } else {
        fmt.Println("键不存在")
    }

    // 遍历顺序是随机的，每次运行可能不同
    for k, v := range m {
        fmt.Println(k, v)        // 顺序不保证
    }

    // 需要有序遍历：先取 key 排序，再按序访问
    keys := make([]string, 0, len(m))
    for k := range m {           // range map 只取 key 时可省略 value
        keys = append(keys, k)
    }
    sort.Strings(keys)
    for _, k := range keys {     // _ 丢弃索引；range slice 第一个值是索引
        fmt.Println(k, m[k])
    }
}
```

### 执行逻辑与数据流向

- `m["不存在"]`：map 找不到键，返回**值类型**的零值。此 map 值类型是 `int`，故返回 `0`。因此单靠返回值无法区分「键不存在」和「键存在且值恰好是 0」——必须用 `val, ok := m[key]`，`ok` 为 `false` 表示键不存在。
- **遍历随机化是 Go 故意设计的**：防止程序员依赖遍历顺序写代码，避免底层实现变动导致集体崩溃。所以「永远不要假设 map 有序」。

### 常见陷阱

- ⚠️ **依赖 map 遍历顺序**：顺序无序且每次运行可能不同。需要有序必须自己排序 key。
- ⚠️ **对 nil map 写入会 panic**：`var m map[string]int` 只声明未初始化（零值 nil），`m["a"]=1` 直接 panic。必须 `m := make(map[string]int)` 或字面量初始化后才能写。读 nil map 不 panic（返回零值）。
- ⚠️ map 的值不可寻址：不能对 `m["k"].field` 直接赋值（若值是 struct）。需整体取出、改、再放回，或用 `map[string]*Struct`（指针）。

---

## 5. struct 与方法、接收者

### 核心概念

struct 是 Go 组织数据的方式（类似 class，但**无继承、无 `__init__`、无 `self`**）。字段首字母**大写=对外可见（导出）**，小写=包内私有。

方法写在 struct **外部**，通过**接收者（receiver）** 绑定，接收者放在函数名前。接收者分两种，是面试分水岭：

- **值接收者 `(u User)`**：方法操作的是**副本**，改不动原对象。适合只读方法。
- **指针接收者 `(u *User)`**：方法操作**原对象**，能修改字段。适合要改状态的方法。

### 代码示例

```go
package main

import "fmt"

type User struct {
    Name string   // 大写：导出，包外可见
    age  int       // 小写：包内私有
}

// 值接收者：改副本，改不动本尊
func (u User) Rename(newName string) {
    u.Name = newName   // 只改了副本
}

// 指针接收者：改本尊
func (u *User) Birthday() {
    u.age++            // 直接改原对象；无需写 (&u).age，Go 自动取地址
}

// 只读方法通常也用指针接收者，保持一致性 & 避免大 struct 拷贝
func (u *User) Greet() string {
    return "我是 " + u.Name
}

func main() {
    u := User{Name: "小明", age: 25}

    u.Rename("小红")          // 值接收者
    fmt.Println(u.Name)      // 小明 —— 没变！改的是副本

    u.Birthday()             // 指针接收者
    fmt.Println(u.age)       // 26 —— 变了，改的是本尊

    fmt.Println(u.Greet())   // 我是 小明
}
```

### 执行逻辑与数据流向

- `u.Rename("小红")`：`(u User)` 是值接收者，调用时 Go 把 `u` **整体拷贝**一份传入。方法内改的是副本的 `Name`，方法结束副本丢弃，外部 `u` 不变——等于白改。
- `u.Birthday()`：`(u *User)` 是指针接收者，传入的是**原对象地址**，`u.age++` 直接改本尊。注意虽然接收者是 `*User`，调用仍写 `u.Birthday()`，Go 自动取地址（语法糖）。

### 常见陷阱

- ⚠️ **想改状态却用了值接收者**：改动丢失，且不报错。判断题「值接收者调 3 次 Inc() 结果是 0，指针接收者是 3」是高频考点。
- ⚠️ **同一类型混用值/指针接收者**：Go 公认坏味道。经验规则：除极小只读 struct 外，**统一用指针接收者**（避免大 struct 拷贝开销 + 保持一致）。

---

# 第二阶段：Go 的灵魂

## 6. 接口 interface

### 核心概念

接口是**一组方法签名的集合**，只规定「要有哪些方法」，不管怎么实现。Go 接口最大特点是**隐式实现**：类型只要拥有接口要求的全部方法，就**自动满足**该接口，无需 `implements` 声明。这是「鸭子类型的编译期版本」——像鸭子走路、像鸭子叫，就是鸭子，但检查提前到编译期。

**核心价值 = 解耦**：接口定义方与实现方彼此不需要知道对方存在。你可以让「你无权修改的类型」（标准库、第三方库类型）满足「你自己定义的接口」。由此衍生 Go 准则：**接口应由使用方定义，而非实现方**。

**关键规则（接收者决定谁满足接口）**：
- 方法用**指针接收者**实现 → **只有指针** `*T` 满足接口（挑）。
- 方法用**值接收者**实现 → **值 `T` 和指针 `*T` 都**满足接口（宽）。

### 代码示例

```go
package main

import "fmt"

// 接口：一组方法集合
type Speaker interface {
    Speak() string
}

type Dog struct{}
func (d Dog) Speak() string { return "汪" }   // 值接收者

type Cat struct{}
func (c Cat) Speak() string { return "喵" }

// 指针接收者的情况
type Robot struct{}
func (r *Robot) Speak() string { return "哔哔" }  // 指针接收者

func main() {
    // 隐式实现：Dog/Cat 从未声明 implements Speaker，但自动满足
    var s Speaker
    s = Dog{}
    fmt.Println(s.Speak())   // 汪
    s = Cat{}
    fmt.Println(s.Speak())   // 喵

    // 接收者规则演示
    // s = Robot{}           // 编译错误！Speak 用指针接收者，值 Robot 不满足
    s = &Robot{}             // 正确：只有 *Robot 满足
    fmt.Println(s.Speak())   // 哔哔

    // 多态：同一接口，不同实现
    speakers := []Speaker{Dog{}, Cat{}, &Robot{}}
    for _, sp := range speakers {
        fmt.Println(sp.Speak())
    }

    // 空接口 any（= interface{}）：无方法要求，任何类型都满足
    printAnything(42)
    printAnything("hello")
    printAnything(Dog{})
}

func printAnything(v any) {   // any 是 interface{} 的别名（Go 1.18+）
    fmt.Println(v)
}
```

### 执行逻辑与数据流向

- `s = Dog{}` 合法，因为 Dog 有 `Speak() string`，编译器在**编译期**确认它满足 Speaker。若少一个方法，直接编译不过。
- `s = Robot{}` 编译错误的原因：`Speak()` 用指针接收者 `(r *Robot)`。一个临时值 `Robot{}` 不保证有稳定地址供指针方法修改，Go 干脆不让值满足这类接口；`&Robot{}`（指针）才满足。
- **为什么这个不对称**：指针接收者的方法可能修改对象——只让指针满足；值接收者方法只读副本，给它指针也能自动解引用取值——所以值和指针都满足（宽进）。

### 常见陷阱

- ⚠️ **用值去满足「指针接收者实现的接口」**：编译报错 `does not implement`。记忆口诀：**指针接收者→只有指针满足（挑）；值接收者→值和指针都满足（宽）**。
- ⚠️ **接口值的 nil 判断**：一个接口变量同时含「类型」和「值」两部分。一个持有 nil 指针但有具体类型的接口值，`iface == nil` 会是 `false`——著名的「nil 接口不为 nil」坑。返回 error 时要小心不要返回一个包了 nil 的接口。

---

## 7. 类型断言与 type switch

### 核心概念

从接口值/`any` 里取回具体类型，用**类型断言** `x.(T)`。直接断言失败会 **panic**；用 **comma-ok** 形式 `v, ok := x.(T)` 则安全（失败返回零值 + `ok=false`，不 panic）。判断多种类型时用 **type switch**。

### 代码示例

```go
package main

import "fmt"

func main() {
    var s any = "hello"

    // 直接断言：失败会 panic
    str := s.(string)
    fmt.Println(str)          // hello
    // n := s.(int)           // panic: interface conversion

    // comma-ok：安全断言，ok 是 bool
    n, ok := s.(int)
    fmt.Println(n, ok)        // 0 false（n 是 int 零值，ok 为 false）

    // type switch：多类型分派
    describe(42)
    describe("go")
    describe(3.14)
    describe(true)
}

func describe(v any) {
    switch x := v.(type) {    // v.(type) 只能用在 switch 里
    case int:
        fmt.Printf("整数 %d\n", x)      // 该分支内 x 的类型是 int
    case string:
        fmt.Printf("字符串 %s\n", x)    // 该分支内 x 是 string
    case float64:
        fmt.Printf("浮点 %.2f\n", x)
    default:
        fmt.Printf("未知类型 %T\n", x)   // %T 打印类型名
    }
}
```

### 执行逻辑与数据流向

- `n, ok := s.(int)`：`s` 底层是 string，断言成 int 失败。返回 `n = 0`（int 零值）、`ok = false`，程序不 panic，继续执行。
- `switch x := v.(type)`：Go 逐个 case 匹配 `v` 的动态类型，命中后 `x` 在该分支内**自动转为对应具体类型**，可直接调用其方法/字段。比 Python 一串 `isinstance()` 优雅。

### 常见陷阱

- ⚠️ **忘用 comma-ok 直接断言**：类型不符时 panic 崩溃。不确定类型时永远用 `v, ok := x.(T)`。
- ⚠️ **混淆 `ok` 的类型**：comma-ok 里的 `ok` **恒为 bool**（`true`/`false`），不是数字。map 查询、类型断言、channel 接收三处的第二返回值都是这个「成没成」的 bool。

---

# 第三阶段：并发

## 8. goroutine

### 核心概念

goroutine 是 Go 的**轻量级线程**，用 `go 函数()` 启动。对比 OS 线程（约 1MB/个）：goroutine 起步仅约 **2KB**，由 **Go 运行时**（非操作系统）调度，可轻松创建**几十万个**。这是 Go 并发能「随便开」的底气。

**关键行为**：`go f()` 启动后 main **不等它，立刻往下走**。而 **main 函数一返回，整个程序退出，所有未跑完的 goroutine 被直接掐死**。因此需要同步机制（WaitGroup / channel）等它们收工。

### 代码示例

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    // 错误示范：main 不等，"你好" 大概率打印不出来
    // go func() { fmt.Println("你好") }()

    // 正确：用 WaitGroup 等一批 goroutine 全部完成
    var wg sync.WaitGroup

    for i := 0; i < 3; i++ {
        wg.Add(1)                 // 计数 +1：登记一个待等待任务
        go func(i int) {          // 用参数接收 i，拷贝一份（关键，见陷阱）
            defer wg.Done()       // 完成时计数 -1（defer 保证一定执行）
            fmt.Println("任务", i)
        }(i)                      // 把当前 i 传进去
    }

    wg.Wait()                     // 阻塞，直到计数归零
    fmt.Println("全部完成")
}
```

### 执行逻辑与数据流向

- `wg.Add(1)` 登记 → goroutine 内 `defer wg.Done()` 使计数递减 → `wg.Wait()` 阻塞 main 直到计数归零。三件套 **Add / Done / Wait** 是「等 N 个并发任务收工」的标准写法。
- `go func(i int){...}(i)`：匿名函数当 goroutine，末尾 `(i)` 立刻调用并传入当前 `i`。参数是**值传递**，每个 goroutine 拿到启动那刻 `i` 的独立拷贝。

### 常见陷阱

- ⚠️ **main 提前退出**：goroutine 还没跑完就被程序退出掐死。必须用 WaitGroup / channel 同步。
- ⚠️ **循环变量捕获（面试明星题）**：若写成闭包直接捕获循环变量 `i`（不传参），在 **Go 1.21 及以前**，多个 goroutine 共享同一个 `i`，等它们执行时循环早已结束，`i` 已是最终值，导致全部打印同一个数（如 `3 3 3`）。
  - **成因**：闭包捕获的是变量本身（引用），不是当时的值快照；goroutine 异步执行，跑到时 for 已转完。
  - **修复**：把 `i` 作为参数传入 `go func(i int){...}(i)`，值传递拷贝一份。
  - **版本注脚**：**Go 1.22 起**每次迭代的循环变量是全新变量，此坑从语言层面修复。面试三点都要答：成因、传参修复、1.22 已修。

---

## 9. channel

### 核心概念

channel 是 goroutine 之间**传数据的管道**。核心哲学：**不要用共享内存来通信，要用通信来共享内存**——让数据通过 channel 传递，谁持有数据谁安全使用，避免抢锁。

- `ch <- x`：发送（箭头指向 ch，数据流入）。
- `x := <-ch`：接收（箭头从 ch 出来，数据流出）。
- **无缓冲 channel** `make(chan T)`：发送和接收**必须同时发生**，否则阻塞。像「当面交接快递」，天然提供同步。
- **有缓冲 channel** `make(chan T, n)`：缓冲区没满就能直接发、没空就能直接收；满了发送才阻塞，空了接收才阻塞。像「快递柜」。

### 代码示例

```go
package main

import "fmt"

func main() {
    // 无缓冲 channel 做同步：main 阻塞等 goroutine 发信号
    done := make(chan string)
    go func() {
        fmt.Println("goroutine 干活中")
        done <- "完成"          // 干完发信号
    }()
    result := <-done            // main 阻塞在此，直到收到信号
    fmt.Println("收到:", result)

    // 有缓冲 channel
    buf := make(chan int, 2)
    buf <- 1                    // 不阻塞
    buf <- 2                    // 不阻塞，缓冲区满
    // buf <- 3                 // 这行会阻塞：缓冲区满且无人接收
    fmt.Println(<-buf, <-buf)   // 1 2

    // 生产者-消费者：for range 持续接收，直到 channel 关闭
    ch := make(chan int)
    go func() {
        for i := 0; i < 3; i++ {
            ch <- i
        }
        close(ch)              // 发送方发完负责 close
    }()
    for v := range ch {        // 一直收，直到 ch 被关闭才结束循环
        fmt.Println("收到", v)  // 0 1 2
    }

    // 从已关闭 channel 接收：comma-ok 判断是否已关闭
    ch2 := make(chan int, 1)
    ch2 <- 100
    close(ch2)
    v, ok := <-ch2
    fmt.Println(v, ok)         // 100 true（还有缓冲值）
    v, ok = <-ch2
    fmt.Println(v, ok)         // 0 false（已取空且关闭）
}
```

### 执行逻辑与数据流向

- 无缓冲同步：main 的 `<-done` 阻塞，直到 goroutine 执行 `done <- "完成"`，两边**同时**完成交接。因此「goroutine 干活中」一定会打印——channel 既传数据又完成同步。
- `for v := range ch`：持续接收，**直到 channel 被 `close`** 才结束。若发送方忘记 close，接收方收完已有数据后会继续等下一个，等不到 → **死锁**。
- 从已关闭 channel 接收：先取完缓冲区剩余值，取空后立即返回**零值**且 `ok=false`，不阻塞。

### 常见陷阱

- ⚠️ **死锁（deadlock）**：所有 goroutine 互相等待、无人推进。Go 运行时检测到会崩溃报 `fatal error: all goroutines are asleep - deadlock!`。典型成因：
  - 无缓冲 channel 在同一 goroutine 内先发后收（发送阻塞，走不到接收）。
  - 发送方忘记 `close`，接收方 `for range` 永远等下一个。
- ⚠️ **close 规则**：**谁发送谁 close**，接收方不要 close；向已关闭 channel **发送会 panic**；重复 close 也 panic。
- ⚠️ **goroutine 泄漏**：goroutine 阻塞在无人接收的 channel 上，永远不退出，长期运行会耗尽资源。

---

## 10. select

### 核心概念

`select` 是 channel 的**多路复用器**：同时等多个 channel，**谁先就绪走谁**；多个同时就绪则**随机**选一个（防依赖设计，同 map 遍历）。最重要的应用是**超时控制**。

### 代码示例

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    ch := make(chan int)
    go func() {
        time.Sleep(3 * time.Second)
        ch <- 42
    }()

    // 超时控制：标准写法
    select {
    case v := <-ch:
        fmt.Println("收到结果", v)
    case <-time.After(2 * time.Second):   // 2 秒后此 channel 自动就绪
        fmt.Println("超时了!")             // 数据要 3 秒 → 走这里
    }

    // 带 default：非阻塞收发
    ch2 := make(chan int)
    select {
    case v := <-ch2:
        fmt.Println("收到", v)
    default:
        fmt.Println("现在没数据，不等了")   // ch2 未就绪 → 立刻走 default
    }
}
```

### 执行逻辑与数据流向

- 超时示例：goroutine 需 3 秒才发数据，`time.After(2s)` 的 channel 在 2 秒时先就绪，`select` 走超时分支。这是给任意操作加「最多等多久」的标准手段。
- `time.After(d)` 返回一个 channel，在 `d` 时长后自动发一个值，因而能作为「计时器 case」。

### 常见陷阱

- ⚠️ **无 default 会阻塞，有 default 不阻塞**：`select` 无 default 时会一直等到某个 case 就绪；加 default 变成「看一眼，没就绪就干别的」。
- ⚠️ **超时后被丢弃的 goroutine**：上例中还在 Sleep 的 goroutine 之后想 `ch <- 42` 时已无人接收——若 ch 无缓冲，该 goroutine 会永久阻塞（泄漏）。生产代码应配合 `context` 取消。
- ⚠️ `select {}`（空 select）会**永久阻塞**当前 goroutine。

---

## 11. sync.Mutex 与并发 bug

### 核心概念

当多个 goroutine 必须读写**同一块共享数据**时，需要**锁**保护。不加保护会产生**竞态条件（race condition）**：结果依赖执行时序、不确定。

**竞态定义**：多个 goroutine 并发读写同一共享数据，且至少有一个是写，最终结果依赖它们的执行时序，导致结果不确定。

修复手段：`sync.Mutex`（互斥锁，锁住临界区）、`sync/atomic`（原子操作，适合简单计数）、或 channel（用通信替代共享）。检测手段：`go test -race` / `go run -race`。

### 代码示例

```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
)

func main() {
    // 无保护 → 竞态，结果往往 < 1000 且每次不同
    // counter++ 不是原子操作：读 → +1 → 写回 三步，可能被其他 goroutine 插入踩踏

    // 修复一：Mutex
    var counter int
    var mu sync.Mutex
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            mu.Lock()          // 加锁：同一时刻只有一个 goroutine 进入临界区
            counter++          // 临界区：读-改-写 不被打断
            mu.Unlock()        // 解锁（实战常用 defer mu.Unlock() 保证释放）
        }()
    }
    wg.Wait()
    fmt.Println("Mutex 结果:", counter)   // 稳定 1000

    // 修复二：atomic（简单计数更轻量，无需锁，由 CPU 指令保证原子性）
    var atomicCounter int64
    var wg2 sync.WaitGroup
    for i := 0; i < 1000; i++ {
        wg2.Add(1)
        go func() {
            defer wg2.Done()
            atomic.AddInt64(&atomicCounter, 1)
        }()
    }
    wg2.Wait()
    fmt.Println("atomic 结果:", atomicCounter)   // 稳定 1000
}
```

### 执行逻辑与数据流向

- **竞态成因**：`counter++` 实为「读取 counter → 加 1 → 写回」三步。goroutine A 读到 5、未写回时，goroutine B 也读到 5；A 写回 6，B 也写回 6——两次自增只涨了 1，**一次自增被吃掉**。1000 次并发反复踩踏，结果 < 1000 且不定。
- **Mutex 修复**：`Lock()` 到 `Unlock()` 之间是**临界区**，同一时刻仅一个 goroutine 进入，其余在 `Lock()` 阻塞排队。「读-改-写」成为不可打断整体，结果稳定。

### 常见陷阱

- ⚠️ **忘记 Unlock**：其他 goroutine 永远卡在 `Lock()`——又是一种死锁。用 `mu.Lock(); defer mu.Unlock()` 保证即便中途 return/panic 也释放。
- ⚠️ **两种并发 bug 对比**（面试收官）：
  - **竞态（race）**：该同步没同步，goroutine 乱抢共享数据 → 结果错乱、不确定。「管得太松」。用锁 / atomic / channel 修。
  - **死锁（deadlock）**：同步过头或用错，goroutine 互相死等 → 程序卡死 `deadlock!`。「管得太死」。成因：channel 无人收/没 close、Mutex 忘 Unlock、多锁交叉等待。
- ⚠️ **测开加分项**：主动说「我会用 `go test -race` 检测数据竞争」——竞态检测器会在运行时报出冲突的行号和 goroutine。

---

# 第四阶段：工程与测试

## 12. go test 与表驱动测试

### 核心概念

Go 测试**内置**，无需第三方框架。规则：
- 测试文件名以 **`_test.go`** 结尾。
- 测试函数以 **`Test`** 开头，参数为 **`*testing.T`**。
- 用 `go test` 运行。
- **无 `assertEqual` 断言**（标准库故意不提供），用普通 `if` 判断，失败调 `t.Errorf`（记录后继续）或 `t.Fatalf`（记录后立即停）。

**表驱动测试（table-driven test）** 是 Go 社区最推崇、面试高频的写法：把所有用例塞进一个切片「表格」，用循环逐个跑，`t.Run` 为每个用例开子测试。惯用命名：期望值叫 `want`，实际值叫 `got`。

### 代码示例

```go
// math.go
package mymath

func Add(a, b int) int      { return a + b }
func IsEven(n int) bool     { return n%2 == 0 }
```

```go
// math_test.go
package mymath

import "testing"

// 基础测试
func TestAdd(t *testing.T) {
    got := Add(2, 3)
    if got != 5 {
        t.Errorf("Add(2,3) = %d; want 5", got)
    }
}

// 表驱动测试（推荐范式）
func TestAddTable(t *testing.T) {
    // 1. 定义表格：匿名 struct 的 slice，每行一个用例
    tests := []struct {
        name string   // 用例名（给 t.Run 用）
        a, b int       // 输入
        want int       // 期望输出
    }{
        {"正数相加", 2, 3, 5},
        {"含负数", -1, 1, 0},
        {"都是零", 0, 0, 0},
    }

    // 2. 循环遍历每个用例
    for _, tt := range tests {
        // 3. t.Run 为每个用例开独立子测试（某个挂了不影响别的）
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d,%d) = %d; want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}

// IsEven 的表驱动测试：期望值字段类型就是 bool
func TestIsEven(t *testing.T) {
    tests := []struct {
        name string
        n    int
        want bool
    }{
        {"4 是偶数", 4, true},
        {"3 是奇数", 3, false},
        {"0 是偶数", 0, true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := IsEven(tt.n); got != tt.want {
                t.Errorf("IsEven(%d) = %v; want %v", tt.n, got, tt.want)
            }
        })
    }
}
```

运行命令：

```
go test              # 跑当前包测试
go test -v           # 显示每个（子）测试详情
go test -race        # 带竞态检测
go test -run TestAdd # 只跑名字匹配的测试
go test -cover       # 显示覆盖率
```

### 执行逻辑与数据流向

- `tests := []struct{...}{...}`：一个匿名 struct 的 slice，每个元素是一组「输入 + 期望输出 + 用例名」。这里融合了 slice（第 3 节）+ struct（第 5 节）。
- `for _, tt := range tests`：range 遍历，`_` 丢弃索引，`tt` 是当前用例。`t.Run(tt.name, ...)` 把每个用例注册为独立子测试，`-v` 下可看到各子测试名与结果；某用例失败不阻断其余用例。

### 常见陷阱

- ⚠️ **测试没被运行**：八成是三条规则破了一条——文件名忘了 `_test`、函数名没大写 `Test` 开头、参数写错不是 `*testing.T`。
- ⚠️ **表格字段冗余**：无需 `id`（`t.Run` 的 name 已足够区分），也无需单独的「是否 bool」字段（期望值字段的**类型**直接声明为 bool 即可）。精简为「name + 输入 + want」。
- ⚠️ **旧版本中子测试内的循环变量捕获**：Go 1.22 前，若在 `t.Run` 的闭包里并行（`t.Parallel()`）使用 `tt`，需 `tt := tt` 拷贝；1.22 后同样已修。

---

# 高频测开面试题速查

> 每题给「标准答案 + 讲解」，可直接背。

### Q1. slice 和数组（array）的区别？

**答**：数组 `[3]int` 长度是类型的一部分、固定不可变，值传递会整个拷贝；slice `[]int` 是对底层数组的引用视图（三件套：指针 + len + cap），长度可变，传递时只拷贝三件套、**共享底层数组**。
**讲解**：关键要点是 `[3]int` 与 `[]int` 是**不同类型**，以及 slice「轻量、共享」的本质。实战几乎只用 slice。

### Q2. `append` 何时触发扩容？怎么扩？

**答**：当 `len == cap`（底层数组满了）时，append 分配更大的新数组、拷贝旧数据、追加新元素、返回指向新数组的新 slice。扩容策略：小容量约**翻倍**，超过约 1024 后按约 **1.25 倍**增长。
**讲解**：记住「翻倍→1.25 倍」的转折，以及「扩容后与原底层数组脱钩」。这解释了为什么必须 `s = append(s, ...)` 赋值回去。

### Q3. 下面输出什么？为什么？

```go
a := []int{1, 2, 3, 4, 5}
b := a[0:2]
b = append(b, 99)
fmt.Println(a)   // ?
```

**答**：`[1 2 99 4 5]`。因为 b 与 a 共享底层数组，b 的 cap 是 5 未满，append 直接写进底层数组索引 2，覆盖了 `a[2]`。
**追问防御**：怎么避免误伤？用三索引切片 `a[0:2:2]` 把 cap 限制为 2，b 满了，append 必然分配新数组，不动 a。

### Q4. map 遍历顺序是固定的吗？

**答**：无序且随机化，每次运行可能不同。Go 故意如此设计，防止程序员依赖遍历顺序。需要有序必须把 key 取出排序后再遍历。
**讲解**：这与 Python 3.7+ dict 保证插入顺序相反，是常见对比考点。

### Q5. Go 为什么没有 try/except？错误怎么处理？

**答**：Go 把错误当作**普通返回值**（`(结果, error)` 模式），要求显式检查 `if err != nil`。理念是错误属于正常控制流，应显式处理，而非当异常藏起来。代价是啰嗦，收益是看代码就知道哪里可能出错，无隐藏崩溃路径。
**讲解**：可提一句 Go 1.13+ 的错误包装 `fmt.Errorf("...: %w", err)` 和 `errors.Is/As` 用于错误链判断。

### Q6. 接口是怎么实现的？和 Java 有什么不同？

**答**：Go 接口是**隐式实现**——类型拥有接口要求的全部方法就自动满足，无需 `implements` 声明。相比 Java 的显式声明，隐式实现让接口定义方与实现方**解耦**，可让无权修改的类型满足自定义接口，接口宜由使用方定义。
**讲解**：关键词是「解耦」和「鸭子类型的编译期版本」。

### Q7. 值接收者和指针接收者对实现接口有什么影响？

**答**：方法用指针接收者实现 → 只有指针 `*T` 满足接口；方法用值接收者实现 → 值 `T` 和指针 `*T` 都满足。
**讲解**：口诀「指针接收者挑（只认指针）、值接收者宽（都认）」。原因：指针方法可能改对象，临时值无稳定地址，故不让值满足。

### Q8. goroutine 和线程的区别？

**答**：goroutine 更轻（起步约 2KB vs 线程约 1MB），由 Go 运行时调度（非 OS），可海量创建（几十万个）。多个 goroutine 复用少量 OS 线程（M:N 调度）。
**讲解**：可补充 GMP 调度模型（Goroutine-Machine-Processor）作为加分。

### Q9. 循环里启动 goroutine 打印循环变量，为什么全是同一个值？

**答**：Go 1.21 及以前，闭包捕获的是循环变量本身（引用），多个 goroutine 共享同一个 `i`；goroutine 异步执行，跑到时循环已结束、`i` 已是最终值，故全部打印同一个数。修复：把 `i` 作为参数传入 goroutine（值拷贝）。Go 1.22 起每次迭代是全新变量，此坑已从语言层面修复。
**讲解**：三点都答（成因、传参修复、1.22 已修）最完整。

### Q10. channel 的无缓冲和有缓冲有什么区别？

**答**：无缓冲 channel 发送和接收必须同时发生（强同步，像当面交接）；有缓冲 channel 缓冲区没满就能直接发、没空就能直接收，满了发送才阻塞、空了接收才阻塞（像快递柜）。
**讲解**：无缓冲的阻塞特性天然提供 goroutine 间同步。

### Q11. 什么是死锁？举例说明。

**答**：所有 goroutine 互相等待、无人能推进，Go 运行时报 `fatal error: all goroutines are asleep - deadlock!`。典型：无缓冲 channel 在同一 goroutine 内先发后收（发送阻塞走不到接收）；发送方忘 close 导致接收方 `for range` 永远等下一个；Mutex 忘 Unlock；多锁交叉等待。
**讲解**：close 规则要点——谁发送谁 close、向已关闭 channel 发送会 panic。

### Q12. 什么是竞态条件？怎么检测和解决？

**答**：多个 goroutine 并发读写同一共享数据、至少一个是写，结果依赖执行时序而不确定。检测：`go test -race` / `go run -race`。解决：`sync.Mutex` 锁临界区、`sync/atomic` 原子操作、或用 channel 通信替代共享。
**讲解**：能解释 `counter++` 非原子（读-改-写三步被踩踏）是加分。「竞态是管得太松，死锁是管得太死」。

### Q13. 怎么给一个操作加超时？

**答**：用 `select` + `time.After`：

```go
select {
case v := <-ch:
    // 正常结果
case <-time.After(2 * time.Second):
    // 超时处理
}
```

**讲解**：生产环境更推荐用 `context.WithTimeout` 传递取消信号，能级联取消下游 goroutine，避免泄漏。

### Q14. 什么是表驱动测试？为什么用它？

**答**：把所有测试用例组织成一个切片「表格」（每行含输入 + 期望输出 + 用例名），用循环逐个跑，`t.Run` 开子测试。好处：测试逻辑与测试数据分离，加用例只需加一行、无需复制代码，用例清晰易维护、覆盖面一目了然，是 idiomatic Go。
**讲解**：能现场手写并说清 `want`/`got` 命名习惯即可。

### Q15. `defer` 的执行时机和常见用途？

**答**：`defer` 注册的函数在**外层函数返回前**执行，多个 defer 按**后进先出（LIFO）** 顺序。常用于资源清理：关闭文件 `defer f.Close()`、解锁 `defer mu.Unlock()`、`defer wg.Done()`。
**讲解**：陷阱——`defer` 的参数在**注册时**求值，但函数体在返回时才执行；循环里大量 defer 会堆积到函数结束才释放。

---

## 附：两条设计主线

1. **「宁可啰嗦，不藏着掖着」**：无隐式类型转换、显式 `if err != nil`、显式接收者、无异常、无继承。Go 用啰嗦换取「读代码即知行为」的确定性。
2. **`value, ok` 惯用法**：map 查询 `v, ok := m[k]`、类型断言 `v, ok := x.(T)`、channel 接收 `v, ok := <-ch`——第二个返回值统一表达「成没成」，`ok` 恒为 bool。见到就条件反射检查它。

---
