import os
import re
import fnmatch
import shutil


class FileAgent:
    
    def __init__(self):
        self.file_types = {
            "pdf": "*.pdf", "txt": "*.txt", "docx": "*.docx", "xlsx": "*.xlsx",
            "jpg": "*.jpg", "png": "*.png", "jpeg": "*.jpeg", "doc": "*.doc",
            "xls": "*.xls", "ppt": "*.ppt", "pptx": "*.pptx"
        }
        
        self.special_paths = {
            'desktop': '~/Desktop', '桌面': '~/Desktop',
            'downloads': '~/Downloads', '下载': '~/Downloads',
            'documents': '~/Documents', '文档': '~/Documents',
            'home': '~', '主目录': '~'
        }
    
    def normalize_path(self, path):
        if not path:
            return None
        
        path = path.strip()
        
        if path.lower() in self.special_paths:
            path = self.special_paths[path.lower()]
        
        return os.path.abspath(os.path.expanduser(path))
    
    def find_files(self, root, pattern, recursive=True):
        root = self.normalize_path(root)
        if not root or not os.path.exists(root):
            return []
        
        matches = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            filenames = [f for f in filenames if not f.startswith('.')]
            
            for filename in filenames:
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.join(dirpath, filename))
            
            if not recursive:
                break
        return matches
    
    def count_hidden_files(self, root):
        root = self.normalize_path(root)
        if not root or not os.path.exists(root):
            return 0
        
        count = 0
        for dirpath, dirnames, filenames in os.walk(root):
            count += sum(1 for f in filenames if f.startswith('.'))
        return count
    
    def create_file_or_folder(self, path, is_folder=False):
        try:
            path = self.normalize_path(path)
            if not path:
                print("❌ 路径无效")
                return False
            
            if is_folder:
                os.makedirs(path, exist_ok=True)
                print(f"✅ 文件夹已创建: {path}")
            else:
                parent_dir = os.path.dirname(path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                
                if os.path.exists(path):
                    print(f"⚠️  文件已存在: {path}")
                    return False
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("")
                print(f"✅ 文件已创建: {path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            return False
    
    def delete_file_or_folder(self, path):
        try:
            path = self.normalize_path(path)
            if not path:
                print("❌ 路径无效")
                return False
            
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"✅ 文件夹已删除: {path}")
            elif os.path.isfile(path):
                os.remove(path)
                print(f"✅ 文件已删除: {path}")
            else:
                print(f"❌ 路径不存在: {path}")
                return False
            return True
            
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False
    
    def modify_file_content(self, path, content):
        try:
            path = self.normalize_path(path)
            if not path:
                print("❌ 路径无效")
                return False
            
            if not os.path.isfile(path):
                print(f"❌ 文件不存在: {path}")
                return False
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 文件内容已修改: {path}")
            return True
            
        except Exception as e:
            print(f"❌ 修改失败: {e}")
            return False
    
    def parse_command(self, cmd):
        match = re.search(r'(.+?)和子目录下所有([a-zA-Z0-9]+)文件', cmd)
        if match:
            folder, ext = match.group(1).strip(), match.group(2).lower()
            if ext in self.file_types:
                return ('find', folder, self.file_types[ext])
            else:
                print(f"❌ 不支持的文件类型: {ext}")
                return None
        
        patterns = [
            r'去\s*(.+?)\s*下面找一下我有多少隐藏文件',
            r'去\s*(.+?)\s*里找一下我有多少隐藏文件',
            r'(.+?)\s*下面有多少隐藏文件'
        ]
        for pattern in patterns:
            match = re.search(pattern, cmd)
            if match:
                folder = match.group(1).strip()
                return ('count', folder)
        
        match = re.search(r'创建一个(.+?)在(.+)', cmd)
        if match:
            item_type, path = match.group(1).strip(), match.group(2).strip()
            is_folder = item_type in ['文件夹', '目录', 'folder']
            return ('create', path, is_folder)
        
        match = re.search(r'删除(.+)', cmd)
        if match:
            path = match.group(1).strip()
            return ('delete', path)
        
        match = re.search(r'修改文件(.+?)的内容为(.+)', cmd)
        if match:
            path, content = match.group(1).strip(), match.group(2).strip()
            return ('modify', path, content)
        
        return None
    
    def execute_command(self, cmd):
        parsed = self.parse_command(cmd)
        if not parsed:
            print("❌ 无法识别指令")
            return False
        
        command_type = parsed[0]
        
        if command_type == 'find':
            _, folder, pattern = parsed
            files = self.find_files(folder, pattern)
            if files:
                print(f"✅ 找到 {len(files)} 个文件:")
                for i, file_path in enumerate(files, 1):
                    print(f"  {i}. {file_path}")
            else:
                print("📭 未找到匹配的文件")
        
        elif command_type == 'count':
            _, folder = parsed
            count = self.count_hidden_files(folder)
            print(f"✅ 找到 {count} 个隐藏文件")
        
        elif command_type == 'create':
            _, path, is_folder = parsed
            self.create_file_or_folder(path, is_folder)
        
        elif command_type == 'delete':
            _, path = parsed
            self.delete_file_or_folder(path)
        
        elif command_type == 'modify':
            _, path, content = parsed
            self.modify_file_content(path, content)
        
        return True
    
    def run(self):
        print("=" * 50)
        print("本地文件Agent")
        print("支持指令:")
        print("1. 查找: 'desktop和子目录下所有pdf文件'")
        print("2. 统计: '去home下面找一下我有多少隐藏文件'") 
        print("3. 创建: '创建一个文件在~/test.txt'")
        print("4. 删除: '删除~/test.txt'")
        print("5. 修改: '修改文件~/test.txt的内容为Hello'")
        print("6. 退出: 'exit'")
        print("=" * 50)
        
        while True:
            try:
                cmd = input("\n请输入指令 > ").strip()
                
                if cmd.lower() in ('exit', 'quit', '退出'):
                    print("再见！")
                    break
                
                if cmd:
                    self.execute_command(cmd)
                    
            except (EOFError, KeyboardInterrupt):
                print("\n程序已退出")
                break


def main():
    agent = FileAgent()
    agent.run()


if __name__ == "__main__":
    main()