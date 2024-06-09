# BilibiliInteractionGraphDnld
Bilibili互动视频剧情树下载。

# `graph.py`
获取b站互动视频的剧情树。

需要准备好`python`、`request`库、`json`库。

运行后，输入bvid，将在运行目录生成一个以aid为名称的文件夹，其中有`config.json`与`file.json`。

*这里斜体代表非官方名称*

## `config.json`格式
- title：视频标题
- aid：视频aid
- advanced：是否开启高级功能
- (开启高级功能)vars：变量
  注意官方文档暂时有误，最近发布的视频的整数变量可能有不只4个
    - 每个变量的键是变量编号(单个字母)
      - name：变量名称
      - type："random"|"normal"，分别对应随机数和整数
      - (非随机数变量)value：初始值
      - (非随机数变量)is_show：是否不隐藏
- root：起始模块在file.json中的键

## `file.json`格式
- 键是一字符串的数字
  - title：模块文案
  - cid：剧情素材的cid
  - type："choice"|"direct"|"leaf"，分别对应分支模块、非分支模块与*结局*模块
  - (非分支模块)"pos"：跳转到的下一个模块的键
  - (启用倒计时功能)default："A"|"B"|"C"|"D"，默认选项
  - A|B|C|D选项
    - text：选项文案
    - pos：分支模块的键
    - (可能有)condition：列表，代表当前选项出现的条件
      - var：变量
      - op："eq"|"ge"|"le"|"ls"|"gt"，分别对应等于、大于等于、小于等于、小于、大于
      - num：值
    - (可能有)change：列表，代表选择选项后的数值变化
      这里减去一个数表示为加上这个数的相反数
      - var：变量
      - op："add"|"set"，分别对应加上(减去相反数)、设置为
      - num：值

# `md.py`

**在`config.json`与`file.json`同目录下**，运行，可以得到一个以aid命名的`.md`文件，有剧情树的`mermaid`图。

# `video.py`

**在`config.json`与`file.json`同目录下**，运行。

可以得到`links.json`，以`cid`为键存储视频直链。

同时得到一个`video`文件夹，以`cid`存储视频的`.mp4`文件。
