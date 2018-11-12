import pygame
import sys
import traceback
from pygame.locals import * 
import myplane
import enemy
import bullet
import supply
from random import *


pygame.init()
pygame.mixer.init()

bg_size = width, height = 480, 700
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption('飞机大战')

# 载入游戏图片
background = pygame.image.load('images/background.png').convert()

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 载入游戏音乐并减小音量
pygame.mixer.music.load("sound/game_music.ogg")
pygame.mixer.music.set_volume(0.2)
bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
bullet_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2)
supply_sound = pygame.mixer.Sound("sound/supply.wav")
supply_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav")
get_bullet_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound("sound/upgrade.wav")
upgrade_sound.set_volume(0.2)
enemy3_fly_sound = pygame.mixer.Sound("sound/enemy3_flying.wav")
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.2)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.5)
me_down_sound = pygame.mixer.Sound("sound/me_down.wav")
me_down_sound.set_volume(0.2)


def hp(each, enmy):
	# 绘制血槽
	pygame.draw.line(screen, BLACK, \
				(each.rect.left, each.rect.top - 5), \
				(each.rect.right, each.rect.top - 5), \
				2)

	# 当生命大于20%显示绿色,否则显示红色
	hp_remain = each.hp / enmy.hp
	if hp_remain > 0.4:
		hp_color = GREEN
	else:
		hp_color = RED
	pygame.draw.line(screen, hp_color, \
				(each.rect.left, each.rect.top - 5), \
				(each.rect.left + each.rect.width * hp_remain, \
				each.rect.top - 5), 2)

def add_small_enemies(group1, group2, num):
	for i in range(num):
		e1 = enemy.SmallEnmy(bg_size)
		group1.add(e1)
		group2.add(e1)

def add_mid_enemies(group1, group2, num):
	for i in range(num):
		e1 = enemy.MidEnmy(bg_size)
		group1.add(e1)
		group2.add(e1)

def add_big_enemies(group1, group2, num):
	for i in range(num):
		e1 = enemy.BigEnmy(bg_size)
		group1.add(e1)
		group2.add(e1)

def inc_speed(target, inc):
	for each in target:
		each.speed += inc


def main():
	# 设置播放通道的最大数
	pygame.mixer.set_num_channels(20)
	pygame.mixer.music.play(-1)

	# 生成我方飞机
	me = myplane.MyPlane(bg_size)
	# 生成普通子弹
	bullet1 = []
	bullet1_index = 0
	BULLET1_NUM = 10
	for i in range(BULLET1_NUM):
		bullet1.append(bullet.Bullet1(me.rect.midtop))

	# 生命数量
	life_image = pygame.image.load('images/life.png').convert_alpha()
	life_rect = life_image.get_rect()
	life_num = 3


	# 生成敌方小、中、大飞机
	enemies = pygame.sprite.Group()
	# 小型敌机
	small_enemies = pygame.sprite.Group()
	add_small_enemies(small_enemies, enemies, 15)
	# 中型敌机
	mid_enemies = pygame.sprite.Group()
	add_mid_enemies(mid_enemies, enemies, 7)
	# 大型敌机
	big_enemies = pygame.sprite.Group()
	add_big_enemies(big_enemies, enemies, 1)

	# 超级子弹定时器
	DOUBLE_BULLET_TIME = USEREVENT + 1

	# 是否使用超级子弹
	is_double_bullet = False

	# 生成超级子弹
	bullet2 = []
	bullet2_index = 0
	BULLET2_NUM = 20
	for i in range(BULLET2_NUM // 2):
		bullet2.append(bullet.Bullet2((me.rect.centerx-33, me.rect.centery)))
		bullet2.append(bullet.Bullet2((me.rect.centerx+30, me.rect.centery)))

	# 用于切换飞机图片
	switch = True
	# 用于控制帧率
	delay = 100

	# 中弹图片索引
	e1_destroy_index = 0
	e2_destroy_index = 0
	e3_destroy_index = 0
	me_destroy_index = 0

	# 统计得分
	score = 0
	# 导入字体样式
	score_font = pygame.font.Font('font/font.ttf', 36)

	# 表示是否暂停游戏
	paused = False
	pause_nor_image = pygame.image.load('images/pause_nor.png').convert_alpha()
	pause_pressed_image = pygame.image.load('images/pause_pressed.png').convert_alpha()
	resume_nor_image = pygame.image.load('images/resume_nor.png').convert_alpha()
	resume_pressed_image = pygame.image.load('images/resume_pressed.png').convert_alpha()
	paused_rect = pause_nor_image.get_rect()
	paused_rect.left, paused_rect.top = width - paused_rect.width - 10, 10
	paused_image = pause_nor_image

	# 设置难度级别
	level = 1

	# 全屏炸弹
	bomb_image = resume_pressed_image = pygame.image.load('images/bomb.png').convert_alpha()
	bobm_image_rect = bomb_image.get_rect()
	bomb_font = pygame.font.Font('font/font.ttf', 48)
	bomb_num = 3

	# 每30秒发放一次补给
	bullet_supply = supply.Bullet_Supply(bg_size)
	bomb_supply = supply.Bomb_Supply(bg_size)
	SUPPLY_TIME = USEREVENT
	pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)

	# 用于阻止重复打开记录文件
	recorded = False

	# 游戏结束画面
	gameover_font = pygame.font.Font('font/font.ttf', 48)

	again_image = pygame.image.load("images/again.png").convert_alpha()
	again_rect = again_image.get_rect()
	gameover_image = pygame.image.load("images/gameover.png").convert_alpha()
	gameover_rect = gameover_image.get_rect()


	# 用于控制帧率
	clock = pygame.time.Clock()


	running = True
	while running:
		for event in pygame.event.get():
			# 检测用户是否关闭窗口
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == MOUSEBUTTONUP:
				if event.button == 1 and paused_rect.collidepoint(event.pos):
					paused = not paused
					if paused:
						pygame.time.set_timer(SUPPLY_TIME, 0)
						pygame.mixer.music.pause()
						pygame.mixer.pause()
					else:
						pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
						pygame.mixer.music.unpause()
						pygame.mixer.unpause()

			elif event.type == MOUSEMOTION:
				if paused_rect.collidepoint(event.pos):
					if paused:
						paused_image = resume_pressed_image
					else:
						paused_image = pause_pressed_image
				else:
					if paused:
						paused_image = resume_nor_image
					else:
						paused_image = pause_nor_image

			elif event.type == KEYUP:
				if event.key == K_SPACE:
					if bomb_num:
						bomb_num -= 1
						bomb_sound.play()
						for each in enemies:
							if each.rect.bottom > 0:
								each.active = False

			elif event.type == SUPPLY_TIME:
				supply_sound.play()
				if choice([True, False]):
					bullet_supply.reset()
				else:
					bomb_supply.reset()

			elif event.type == DOUBLE_BULLET_TIME:
				is_double_bullet = False
				pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)



		# 根据用户的得分增加难度
		if level == 1 and score > 500:
			level = 2
			upgrade_sound.play()
			# 增加5架小型机,3架中型机,1架大型机
			add_small_enemies(small_enemies, enemies, 5)
			add_mid_enemies(mid_enemies, enemies, 3)
			add_big_enemies(big_enemies, enemies, 1)

		elif level == 2 and score > 1500:
			level = 3
			upgrade_sound.play()
			# 增加5架小型机,3架中型机,1架大型机
			add_small_enemies(small_enemies, enemies, 5)
			add_mid_enemies(mid_enemies, enemies, 3)
			add_big_enemies(big_enemies, enemies, 1)
			# 提升飞机型机的速度
			inc_speed(small_enemies, 1)

		elif level == 3 and score > 3000:
			level = 4
			upgrade_sound.play()
			# 增加5架小型机,3架中型机,1架大型机
			add_small_enemies(small_enemies, enemies, 5)
			add_mid_enemies(mid_enemies, enemies, 3)
			add_big_enemies(big_enemies, enemies, 1)
			inc_speed(small_enemies, 1)
			inc_speed(mid_enemies, 1)

		elif level == 4 and score > 5000:
			level = 5
			upgrade_sound.play()
			# 增加5架小型机,3架中型机,1架大型机
			add_small_enemies(small_enemies, enemies, 5)
			add_mid_enemies(mid_enemies, enemies, 3)
			add_big_enemies(big_enemies, enemies, 1)
			inc_speed(small_enemies, 1)
			inc_speed(mid_enemies, 1)
			inc_speed(big_enemies, 1)


		# 绘制背景
		screen.blit(background, (0, 0))

		if life_num and not paused:
			# 检测用户的键盘操作
			key_pressed = pygame.key.get_pressed()

			if key_pressed[K_w] or key_pressed[K_UP]:
				me.moveUp()
			if key_pressed[K_s] or key_pressed[K_DOWN]:
				me.moveDown()
			if key_pressed[K_a] or key_pressed[K_LEFT]:
				me.moveLeft()
			if key_pressed[K_d] or key_pressed[K_RIGHT]:
				me.moveRight()

			# 绘制全屏炸弹补给并检测玩家是否获得
			if bomb_supply.active:
				bomb_supply.move()
				screen.blit(bomb_supply.image, bomb_supply.rect)
				if pygame.sprite.collide_mask(bomb_supply, me):
					get_bomb_sound.play()
					if bomb_num < 3:
						bomb_num += 1
					bomb_supply.active = False

			# 绘制超级子弹补给并检测玩家是否获得
			if bullet_supply.active:
				bullet_supply.move()
				screen.blit(bullet_supply.image, bullet_supply.rect)
				if pygame.sprite.collide_mask(bullet_supply, me):
					get_bullet_sound.play()
					# 发射超级子弹
					is_double_bullet = True
					pygame.time.set_timer(DOUBLE_BULLET_TIME, 20 * 1000)
					bullet_supply.active = False

			# 发射子弹
			if not(delay % 5):
				bullet_sound.play()
				if is_double_bullet:
					bullets = bullet2
					bullets[bullet2_index].reset((me.rect.centerx-33, me.rect.centery))
					bullets[bullet2_index+1].reset((me.rect.centerx+30, me.rect.centery))
					bullet2_index = (bullet2_index + 2) % BULLET2_NUM
				else:
					bullets = bullet1
					bullets[bullet1_index].reset(me.rect.midtop)
					bullet1_index = (bullet1_index + 1) % BULLET1_NUM

			# 检测子弹是否击中敌机
			for b in bullets:
				if b.active:
					b.move()
					screen.blit(b.image, b.rect)
					enemy_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
					if enemy_hit:
						b.active = False
						for e in enemy_hit:
							if e in mid_enemies or e in big_enemies:
								e.hit = True
								e.hp -= 1
								if e.hp == 0:
									e.active = False
							else:
								e.hp -= 1
								if e.hp == 0:
									e.active = False
							
			# 绘制敌机(大)
			for each in big_enemies:
				if each.active:
					each.move()
					if each.hit == True:
						# 绘制被打到的特效
						screen.blit(each.image_hit, each.rect)
						each.hit = False
					else:
						if switch:
							screen.blit(each.image1, each.rect)
						else:
							screen.blit(each.image2, each.rect)

					# 绘制血槽
					hp(each, enemy.BigEnmy)

					# 敌机出现开始播放音效
					if each.rect.bottom == -50:
						enemy3_fly_sound.play(-1)
				else:
					# 毁灭
					if not(delay % 3):
						if e3_destroy_index == 0:
							enemy3_fly_sound.stop()
							enemy3_down_sound.play()
						screen.blit(each.destroy_images[e3_destroy_index], each.rect)
						e3_destroy_index = (e3_destroy_index + 1) % 6
						if e3_destroy_index == 0:
							score += 100
							each.reset()
			# 绘制敌机(中)
			for each in mid_enemies:
				if each.active:
					each.move()
					if each.hit == True:
						# 绘制被打到的特效
						screen.blit(each.image_hit, each.rect)
						each.hit = False
					else:
						screen.blit(each.image, each.rect)

					# 绘制血槽
					hp(each, enemy.MidEnmy)
				else:
					# 毁灭
					if not(delay % 3):
						if e2_destroy_index == 0:
							enemy2_down_sound.play()
						screen.blit(each.destroy_images[e2_destroy_index], each.rect)
						e2_destroy_index = (e2_destroy_index + 1) % 4
						if e2_destroy_index == 0:
							score += 60
							each.reset()
			# 绘制敌机(小)
			for each in small_enemies:
				if each.active:
					each.move()
					screen.blit(each.image, each.rect)

					# 绘制血槽
					hp(each, enemy.SmallEnmy)
				else:
					# 毁灭				
					if not(delay % 3):
						if e1_destroy_index == 0:
							enemy1_down_sound.play()
						screen.blit(each.destroy_images[e1_destroy_index], each.rect)
						e1_destroy_index = (e1_destroy_index + 1) % 4
						if e1_destroy_index == 0:
							score += 10
							each.reset()

			# 检测我方飞机是否被撞
			enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
			if enemies_down:
				me.active = False
				for e in enemies_down:
					e.active = False

			# 绘制我方飞机
			if me.active:
				if switch:
					screen.blit(me.image1, me.rect)
				else:
					screen.blit(me.image2, me.rect)
			else:
				# 我方飞机毁灭		
				if not(delay % 3):
					if me_destroy_index == 0:
						me_down_sound.play()
					screen.blit(me.destroy_images[me_destroy_index], me.rect)
					me_destroy_index = (me_destroy_index + 1) % 4
					if me_destroy_index == 0:
						# 释放全屏炸弹并复活
						for each in enemies:
							if each.rect.bottom > 0:
								each.active = False
						life_num -= 1
						me.reset()
			# 绘制得分
			score_text = score_font.render('Score : %s' % str(score), True, WHITE)
			screen.blit(score_text, (10, 5))

		# 绘制游戏结束
		elif life_num == 0:
			# 背景音乐停止
			pygame.mixer.music.stop()
			# 停止所有音效
			pygame.mixer.stop()
			# 停止发放补给
			pygame.time.set_timer(SUPPLY_TIME, 0)

			if not recorded:
				# 读取历史最高得分
				with open('record.txt', 'r') as f:
					record_score = int(f.read())

				# 如果本次得分高于历史最高, 则存档
				if score > record_score:
					with open('record.txt', 'w') as f:
						f.write(str(score))
				recorded = True

			# 绘制结束界面
			record_score_text = score_font.render("Best : %d" % record_score, True, (255, 255, 255))
			screen.blit(record_score_text, (50, 50))
			
			gameover_text1 = gameover_font.render("Your Score", True, (255, 255, 255))
			gameover_text1_rect = gameover_text1.get_rect()
			gameover_text1_rect.left, gameover_text1_rect.top = \
								 (width - gameover_text1_rect.width) // 2, height // 3
			screen.blit(gameover_text1, gameover_text1_rect)
			
			gameover_text2 = gameover_font.render(str(score), True, (255, 255, 255))
			gameover_text2_rect = gameover_text2.get_rect()
			gameover_text2_rect.left, gameover_text2_rect.top = \
								 (width - gameover_text2_rect.width) // 2, \
								 gameover_text1_rect.bottom + 10
			screen.blit(gameover_text2, gameover_text2_rect)

			again_rect.left, again_rect.top = \
							 (width - again_rect.width) // 2, \
							 gameover_text2_rect.bottom + 50
			screen.blit(again_image, again_rect)

			gameover_rect.left, gameover_rect.top = \
								(width - again_rect.width) // 2, \
								again_rect.bottom + 10
			screen.blit(gameover_image, gameover_rect)

			# 检测用户的鼠标操作
			# 如果用户按下鼠标左键
			if pygame.mouse.get_pressed()[0]:
				# 获取鼠标坐标
				pos = pygame.mouse.get_pos()
				# 如果用户点击“重新开始”
				if again_rect.left < pos[0] < again_rect.right and \
				   again_rect.top < pos[1] < again_rect.bottom:
					# 调用main函数，重新开始游戏
					main()
				# 如果用户点击“结束游戏”            
				elif gameover_rect.left < pos[0] < gameover_rect.right and \
					 gameover_rect.top < pos[1] < gameover_rect.bottom:
					# 退出游戏
					pygame.quit()
					sys.exit()


		# 绘制暂停按钮
		screen.blit(paused_image, paused_rect)

		# 绘制剩余炸弹数量
		bomb_text = score_font.render('× %d' % bomb_num, True, WHITE)
		bomb_text_rect = bomb_text.get_rect()
		screen.blit(bomb_image, (10, height - 10 - bomb_text_rect.height))
		screen.blit(bomb_text, (20 + bobm_image_rect.width, height - 5 - bomb_text_rect.height))

		# 绘制剩余生命数量
		if life_num:
			for i in range(life_num):
				screen.blit(life_image, \
						(width - 10 - (i + 1) * life_rect.width, \
						height - 10 - life_rect.height))

		# 控制飞机图片切换速度
		if not(delay % 5):
			switch = not switch

		delay -= 1
		if not delay:
			delay = 100

		# 从缓冲区更新到屏幕
		pygame.display.flip()
		# 设置不会超过每秒60帧
		clock.tick(60)


if __name__ == '__main__':
	try:
		main()
	except SystemExit:
		pass
	except:
		traceback.print_exc();
		pygame.quit()
		input()
