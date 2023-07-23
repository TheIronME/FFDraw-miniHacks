import glm
import glfw
from ff_draw.gui.text import TextPosition
from ff_draw.plugins import FFDrawPlugin
import imgui
from nylib.utils.win32 import memory as ny_mem

from pynput import keyboard

shell_uninstall = '''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
uninstall(key)
'''
shell_uninstall_multi = '''
def uninstall_multi(key):
    if hasattr(inject_server, key):
        for hook in getattr(inject_server, key):
            hook.uninstall()
        delattr(inject_server, key)
'''

shell='''
from nylib.hook import create_hook
from ctypes import c_int64, c_float, c_ubyte, c_uint,c_void_p,addressof
def create_knock_hook():
    if hasattr(inject_server, key):
        return addressof(getattr(getattr(inject_server, key), 'val'))
    val = c_float(0)
    def knock_hook(hook, actor_ptr, angle, dis, knock_time, a5, a6):
        print(f"get_hooked_message {str(actor_ptr)} ")
        return hook.original(actor_ptr, 0, 0, 0, a5, a6)
    hook = create_hook(actorKnockAdress, c_int64, [c_int64, c_float, c_float, c_int64, c_ubyte, c_uint])(knock_hook).install_and_enable()
    setattr(hook, 'val', val)
    setattr(inject_server, key, hook)
    return addressof(val)
res=create_knock_hook()
'''

class MiniHack(FFDrawPlugin):
    def __init__(self, main):
        super().__init__(main)
        self.print_name = self.data.setdefault('print_name', True)
        self.show_imgui_window = True
        self.main=main
        self.me=main.mem.actor_table.me
        self.mem = main.mem
        
        self.keyboardListener=keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
        self.keyboardListener.start()
        
        
        self.tp=False
        self.x=0
        self.y=0
        self.z=0
        
        self.actionNoMoveStatus=False
        self.actionNoMoveAdress = self.mem.scanner.find_address("48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B F1 0F 29 74 24 ? 48 8B 89 ? ? ? ? 0F 28 F3")
        self.actionNoMoveRaw=self.mem.scanner.get_original_text(self.actionNoMoveAdress, 1)[0]
        
        self.antiKnock=False
        self.actorKnockAdress = self.mem.scanner.find_address("48 8B C4 48 89 70 ? 57 48 81 EC ? ? ? ? 0F 29 70 ? 0F 28 C1")
        self.actorKnockKey='__hacks_hook__actorKnock__'
        

    def on_press(self,key):

        if key == keyboard.Key.left  :
            self.moveX()
        elif key == keyboard.Key.right :
            self.moveY()
        elif key == keyboard.Key.up    :
            self.moveZ()
        elif key == keyboard.Key.down  :
            self.moveZ(-1)


    def on_release(self,key):
        pass

        

    def draw_panel(self):
        if not self.show_imgui_window: return
        
        if imgui.button('突进无位移') :
            if  not self.actionNoMoveStatus :
                self.setActionNoMove(True)
            else :
                self.setActionNoMove(False)
            self.actionNoMoveStatus=not self.actionNoMoveStatus
        imgui.same_line()
        imgui.text(f'突进无位移状态：{"开启" if self.actionNoMoveStatus else "关闭"}')   
        
         
        if imgui.button('防击退') :
            if not self.antiKnock:
                self.actorKnockHook=self.mem.inject_handle.run(f'key=\'{self.actorKnockKey}\'\nactorKnockAdress = {self.actorKnockAdress}\n' + shell)
            else:
                self.mem.inject_handle.run(f'key =\'{self.actorKnockKey}\'\n' + shell_uninstall)   
            self.antiKnock=not self.antiKnock
        imgui.same_line()
        imgui.text(f'防击退状态：{"开启" if self.antiKnock else "关闭"}')   
        
        
        
        if imgui.button('tp开关') :
            self.tp=not self.tp
        imgui.same_line()
        imgui.text(f'tp开关状态：{"开启" if self.tp else "关闭"}')    
        
        
        if imgui.button('X+1') :
            self.moveX()
        imgui.same_line()
        if imgui.button('X-1') :
            self.moveX(-1)
            
        if imgui.button('Y+1') :
            self.moveY()
        imgui.same_line()
        if imgui.button('Y-1') :
            self.moveY(-1)
            
            
        if imgui.button('Z+1') :
            self.moveZ()
        imgui.same_line()
        if imgui.button('Z-1') :
            self.moveZ(-1)


        
    def moveX(self,value=1):
        toPos=self.me.pos
        toPos.x+=value
        self.writePos(toPos)
    def moveY(self,value=1):
        toPos=self.me.pos
        toPos.z+=value
        self.writePos(toPos)
    def moveZ(self,value=1):
        toPos=self.me.pos
        toPos.y+=value
        self.writePos(toPos) 
        
        
        
        
    def writePos(self,toPos:glm.vec3)  :    
        if self.tp:    
            ny_mem.write_bytes(self.me.handle, self.me.address + self.me.offsets.pos, toPos.to_bytes())
        
        

    
    def getPos(self):
        return bytes(ny_mem.read_bytes(self.me.handle, self.me.address + self.me.offsets.pos, 0xc))

    def update(self, main):
        meAdress=self.me.address + self.me.offsets.pos
        #print(hex(meAdress))
            
            
    def setActionNoMove(self, mode):
        
        ny_mem.write_ubyte(self.me.handle,self.actionNoMoveAdress, 0xc3 if mode else self.actionNoMoveRaw)



