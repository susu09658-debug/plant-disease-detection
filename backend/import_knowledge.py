import os
import django

# 1. 初始化 Django 环境
# ⚠️ 注意：把 'your_project_name.settings' 替换为你实际的 settings 路径
# 如果你的 manage.py 里写的是 os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')，那就填 'backend.settings'
# 修改后：
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

# 2. 导入你的模型
# ⚠️ 注意：假设你的应用名叫 knowledge，模型名叫 KnowledgeInfo，请根据实际情况修改
from apps.knowledge.models import KnowledgeInfo

# 3. 准备好的丰富数据
knowledge_data = [
    # ---- 木薯类 ----
    {"plant": "木薯", "disease": "细菌性枯萎病", "severity": 4,
     "symptom": "叶片出现水渍状角斑，随后变为褐色，叶片萎蔫下垂，茎秆可能流出黄色胶状物。",
     "treatment": "种植抗病品种；实行轮作；发现病株及时拔除并销毁；发病初期喷洒农用链霉素。"},
    {"plant": "木薯", "disease": "褐斑病", "severity": 2,
     "symptom": "叶片上出现明显的褐色圆形病斑，边缘颜色较深，严重时叶片发黄脱落。",
     "treatment": "加强田间通风透光；发病初期喷洒代森锰锌或波尔多液进行防治。"},
    {"plant": "木薯", "disease": "健康", "severity": 1, "symptom": "植株生长旺盛，叶片翠绿，无明显病斑或虫咬痕迹。",
     "treatment": "保持良好的水肥管理，定期巡查，做好预防即可。"},
    {"plant": "木薯", "disease": "花叶病", "severity": 5,
     "symptom": "叶片褪绿，呈现黄绿相间的花叶斑驳，叶片畸形皱缩，植株严重矮化，产量大幅下降。",
     "treatment": "主要由粉虱传播，需重点防治粉虱；必须拔除并烧毁病株；使用无毒种苗种植。"},
    {"plant": "木薯", "disease": "根腐病", "severity": 4,
     "symptom": "地上部分生长停滞，叶片发黄脱落；地下块根腐烂发黑，散发难闻的腐臭味。",
     "treatment": "选择地势高燥、排水良好的地块种植；雨季注意挖沟排水；播种前进行土壤消毒。"},

    # ---- 玉米类 ----
    {"plant": "玉米", "disease": "褐斑病", "severity": 3,
     "symptom": "主要发生在叶片和叶鞘上，出现密集的小圆形红褐色斑点，病斑常连成一片。",
     "treatment": "合理密植，增施磷钾肥；发病初期喷洒三唑酮或粉锈宁。"},
    {"plant": "玉米", "disease": "炭疽病", "severity": 3,
     "symptom": "叶片上出现梭形或不规则形的轮纹病斑，边缘红褐色，中央灰白色，后期病斑易破裂。",
     "treatment": "清除田间病残体；发病初期使用多菌灵或咪鲜胺进行叶面喷施。"},
    {"plant": "玉米", "disease": "褪绿叶斑病", "severity": 2,
     "symptom": "叶片上出现沿叶脉扩展的褪绿条纹或斑块，光合作用受到一定影响。",
     "treatment": "选择抗病品种；注意补充微量元素，增强植株抗性。"},
    {"plant": "玉米", "disease": "灰斑病", "severity": 4,
     "symptom": "叶片上形成矩形或长条形灰褐色病斑，病斑与叶脉平行，高湿环境下病斑背面会产生灰色霉层。",
     "treatment": "收获后深翻土壤；发病初期喷洒代森锰锌、百菌清等杀菌剂。"},
    {"plant": "玉米", "disease": "健康", "severity": 1, "symptom": "茎秆挺拔，叶片宽大舒展、颜色浓绿，长势均匀一致。",
     "treatment": "正常进行田间水肥管理与除草。"},
    {"plant": "玉米", "disease": "虫害", "severity": 3,
     "symptom": "叶片出现缺刻、孔洞，或心叶被咬食（常见草地贪夜蛾、玉米螟等），可能伴有虫粪。",
     "treatment": "使用杀虫灯诱杀成虫；化学防治可选用氯虫苯甲酰胺、甲维盐等药剂喷雾心叶。"},
    {"plant": "玉米", "disease": "霉病", "severity": 4,
     "symptom": "主要发生在果穗上，籽粒间长出白色或粉色、绿色的霉层，导致籽粒腐烂。",
     "treatment": "适期晚播，避开抽雄吐丝期的连阴雨；成熟后及时收获并晾晒干燥。"},
    {"plant": "玉米", "disease": "紫色变色", "severity": 2,
     "symptom": "苗期叶片或茎秆发紫，通常与低温导致根系吸收磷元素受阻有关。",
     "treatment": "随着气温回升通常能自行缓解；也可叶面喷施磷酸二氢钾补充营养。"},
    {"plant": "玉米", "disease": "黑穗病", "severity": 5,
     "symptom": "果穗或雄穗被破坏，形成巨大的黑粉瘤，破裂后散发大量黑褐色粉末（病原菌孢子）。",
     "treatment": "属于系统性侵染病害。必须使用种衣剂包衣播种；发现病瘤在破裂前立即套袋拔除销毁。"},
    {"plant": "玉米", "disease": "条纹病", "severity": 3,
     "symptom": "叶脉间出现连续或断续的褪绿黄色细条纹，严重时叶片发白枯死。",
     "treatment": "由叶蝉等害虫传毒，需及时防治田间害虫，清除杂草切断毒源。"},
    {"plant": "玉米", "disease": "条斑病", "severity": 3,
     "symptom": "叶片上出现水渍状、半透明的窄长条斑，后变为黄褐色或红褐色。",
     "treatment": "细菌性病害，发病初期可喷洒中生菌素或农用链霉素。"},
    {"plant": "玉米", "disease": "紫罗兰变色", "severity": 2,
     "symptom": "植株表现出异常的紫红色，类似紫色变色，多为环境胁迫（缺素、积水、冷害）引起。",
     "treatment": "查明原因，疏通田间排水，增施腐熟有机肥和磷钾肥。"},
    {"plant": "玉米", "disease": "黄斑病", "severity": 3,
     "symptom": "叶片上出现散生的黄色或淡黄色斑点，逐渐扩大导致叶片局部枯黄。",
     "treatment": "发病初期使用戊唑醇或吡唑醚菌酯进行喷雾防治。"},
    {"plant": "玉米", "disease": "黄化病", "severity": 3,
     "symptom": "植株整体或中下部叶片发黄，生长迟缓，可能是缺氮或根系发育不良。",
     "treatment": "及时追施尿素等速效氮肥，或使用氨基酸叶面肥喷施缓解。"},
    {"plant": "玉米", "disease": "叶枯病", "severity": 4,
     "symptom": "病害常从下部叶片开始，大面积枯死干黄，向上蔓延迅速，严重影响灌浆。",
     "treatment": "种植抗病品种；发病初期及时喷洒退菌特或代森锌。"},
    {"plant": "玉米", "disease": "锈病叶", "severity": 3,
     "symptom": "叶片正反两面出现散生的红褐色突起疱斑（夏孢子堆），破裂后散发铁锈色粉末。",
     "treatment": "发病初期及时喷洒三唑酮、粉锈宁或苯醚甲环唑。"},

    # ---- 番茄类 ----
    {"plant": "番茄", "disease": "褐斑病", "severity": 3,
     "symptom": "叶片上出现近圆形褐色病斑，病斑上常有同心轮纹，高湿时有黑色霉状物。",
     "treatment": "加强通风降低湿度；发病初期喷洒代森锰锌或异菌脲。"},
    {"plant": "番茄", "disease": "细菌性萎蔫病", "severity": 5,
     "symptom": "植株顶部叶片白天萎蔫，早晚恢复，随后整株迅速青枯死亡。横切病茎挤压有乳白色菌脓溢出。",
     "treatment": "极其顽固。必须实行轮作；土壤需用石灰或生防菌消毒；发病初期灌根农用链霉素，病株带土拔除。"},
    {"plant": "番茄", "disease": "疫病叶", "severity": 4,
     "symptom": "晚疫病特征，叶片边缘出现水浸状暗绿色大斑，迅速蔓延，高湿环境病斑边缘会长出白色霉圈。",
     "treatment": "控制大棚湿度；发病前使用百菌清预防，发病后选用甲霜灵或霜脲锰锌进行扑杀。"},
    {"plant": "番茄", "disease": "健康", "severity": 1, "symptom": "茎秆粗壮，叶片羽状深裂、颜色浓绿舒展，花果发育正常。",
     "treatment": "保持科学的温湿度管理，合理整枝打杈。"},
    {"plant": "番茄", "disease": "花叶病毒", "severity": 4,
     "symptom": "顶端新叶出现明脉和褪绿，随后形成浓淡相间的斑驳花叶，叶片变小皱缩，果实常有坏死斑。",
     "treatment": "病毒病无特效药。重点在于前期灭蚜防病；发病初期喷洒氨基寡糖素、宁南霉素钝化病毒。"},
    {"plant": "番茄", "disease": "黄化曲叶病毒", "severity": 5,
     "symptom": "毁灭性病害（TY病毒）。上部叶片明显变小、发黄增厚、边缘向上卷曲，植株严重矮化，开花不结果。",
     "treatment": "首选种植抗TY病毒品种；在大棚通风口加设防虫网，使用黄板诱杀并喷药彻底消灭传毒媒介烟粉虱。"}
]


def import_data():
    print("开始导入知识库数据...")
    count = 0
    for item in knowledge_data:
        # 使用 get_or_create 避免重复运行脚本导致数据重复
        obj, created = KnowledgeInfo.objects.get_or_create(
            plant_name=item["plant"],
            disease_name=item["disease"],
            defaults={
                'severity': item["severity"],
                'symptom': item["symptom"],
                'treatment': item["treatment"],
                'image_url': ''  # 图片留空
            }
        )
        if created:
            count += 1
            print(f"✅ 成功导入: {item['plant']} - {item['disease']}")
        else:
            print(f"⚠️ 已存在，跳过: {item['plant']} - {item['disease']}")

    print(f"\n🎉 导入完成！共新增了 {count} 条数据。")


if __name__ == "__main__":
    import_data()