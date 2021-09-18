<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns="http://www.w3.org/1999/xhtml">
<xsl:output encoding="UTF-8" method="html"
	doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
	doctype-system="DTD/xhtml1-transitional.dtd"/>

<!-- 作成: 中山智哉 井上義勝 傳智之   -->
<!-- 変更: 2005.03.16             -->
<!-- 最終変更: 2009.07.02 高野知子 50-53,77-106コメントアウト, ファイル名をcorrection.xslから変更 -->


<!-- 変数 -->
<xsl:variable name="correct_color">#ff0000</xsl:variable>
<xsl:variable name="better_color">#0000ff</xsl:variable>
<xsl:variable name="unclear_color">#008000</xsl:variable>
<xsl:variable name="comment_color">#008000</xsl:variable>
<xsl:variable name="margin">margin:0.2em;</xsl:variable>
<xsl:variable name="padding">padding:0.2em;</xsl:variable>
<xsl:variable name="font-weight">font-weight:bold;</xsl:variable>
<xsl:variable name="font-family">font-family:'MS Gothic';</xsl:variable>


<xsl:template match="/">
<html lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<title>作文コーパス 添削情報表示 <xsl:value-of select="composition/title"/></title>
<script language="javascript">
function display(id){
	if (document.all) OBJ = document.all(id).style;
	else if (document.getElementById) OBJ = document.getElementById(id).style;
	if (OBJ) OBJ.display=='none'?OBJ.display='':OBJ.display='none';
}
</script>
<style type="text/css">
body{color:#000000;background:#fff1df;padding:1em;margin:0em}
a{text-decoration:none}
a:hover{color:#ffffff;background:#ff4040}
table{border-collapse:collapse}
#info{border:1px #ffffff solid;border-collapse:collapse}
#info th{color:#ffffff;background:#808080}
#tag_summary th, #tag_summary td{border:1px #000000 solid;width:12%}
#tag_summary th{color:#ffffff;background:#808080}
</style>
</head>
<body>

<!-- <table>
<tr><th>執筆者ID</th><td><xsl:value-of select="composition/writer"/></td></tr>
<tr><th>添削者ID</th><td><xsl:value-of select="composition/revisor"/></td></tr>
</table>  -->

<div style="background:#ffffff;line-height:5em;padding:1em 2em;margin:1em;border:1px #484800 solid">
	<xsl:apply-templates/>

	<xsl:if test="//review">
		<div>
			<xsl:attribute name="style">
				<xsl:value-of select="$margin"/>
				border: 1px <xsl:value-of select="$comment_color"/> solid;
				<xsl:value-of select="$padding"/>
				color:<xsl:value-of select="$comment_color"/>;
				line-height:1em;
			</xsl:attribute>
			<span style="font-weight:bold">【総評】</span>
			<ul>
			<xsl:for-each select="//review">
				<li><xsl:value-of select="@comment"/></li>
			</xsl:for-each>
			</ul>
		</div>
	</xsl:if>
</div>

<!--  <a href="javascript:display('tag_summary')">添削タグの詳細...</a>
<table id="tag_summary" style="display:none">
<tr>
	<th></th>
	<th title="correct">訂正</th>
	<th title="better">提案</th>
	<th title="unclear">不明瞭</th>
	<th title="newparagraph">改行</th>
	<th title="runon">追込</th>
	<th title="review">総評</th>
</tr>
<tr>
	<th>タグ数</th>
	<td><xsl:value-of select="count(composition/essay/correct)"/></td>
	<td><xsl:value-of select="count(composition/essay/better)"/></td>
	<td><xsl:value-of select="count(composition/essay/unclear)"/></td>
	<td><xsl:value-of select="count(composition/essay/newparagraph)"/></td>
	<td><xsl:value-of select="count(composition/essay/runon)"/></td>
	<td><xsl:value-of select="count(composition/essay/review)"/></td>
</tr>
<tr>
	<th>コメント付</th>
	<td><xsl:value-of select="count(composition/essay/correct[@comment != ''])"/></td>
	<td><xsl:value-of select="count(composition/essay/better[@comment != ''])"/></td>
	<td><xsl:value-of select="count(composition/essay/unclear[@comment != ''])"/></td>
	<td><xsl:value-of select="count(composition/essay/newparagraph[@comment != ''])"/></td>
	<td><xsl:value-of select="count(composition/essay/runon[@comment != ''])"/></td>
	<td><xsl:value-of select="count(composition/essay/review[@comment != ''])"/></td>
</tr>
</table>  -->

</body>
</html>
</xsl:template>


<!-- 調べなさい 2005.03.16 -->
<xsl:template match="//search">
	<a>
	<xsl:attribute name="href">
	<xsl:choose>
		<xsl:when test="@value [. = 'infoseek_kokugo']">
			<xsl:text>http://jiten.www.infoseek.co.jp/Kokugo?pg=result_k.html&amp;col=KO&amp;sm=1&amp;qt=</xsl:text>
			<xsl:apply-templates/>
			<xsl:text>&amp;svp=SEEK&amp;svx=100600</xsl:text>
		</xsl:when>
		<xsl:otherwise>
			<xsl:text>http://www.google.co.jp/search?q="</xsl:text>
			<xsl:apply-templates/>
			<xsl:text>"&amp;hl=ja&amp;lr=lang_ja&amp;ie=utf-8&amp;oe=utf-8</xsl:text>
		</xsl:otherwise>
	</xsl:choose>
	</xsl:attribute>
	<xsl:apply-templates/>
	</a>

	<span style="color:#8f8f00;position:relative;top:-1.5em;left:-1.5em;font-size:smaller;margin:0.2em">
	<xsl:choose>
		<xsl:when test="@value [. = 'infoseek_kokugo']">Infoseek国語辞典</xsl:when>
		<xsl:otherwise>Google</xsl:otherwise>
	</xsl:choose>
	</span>
</xsl:template>


<!-- 訂正 2005.03.17 -->
<xsl:template match="//correct">
	<!-- 削除・置換 -->
	<!-- spanを二重にすると打消線だけ赤くできる -->
	<!-- http://www.mozilla.gr.jp/standards/webtips0002.html 参照 -->
	<xsl:if test="string-length(.)">
		<span>
			<xsl:attribute name="style">
				color:<xsl:value-of select="$correct_color"/>;
				<xsl:value-of select="$padding"/>
				<xsl:value-of select="$font-weight"/>
				text-decoration:line-through;
			</xsl:attribute>

			<span style="color:#000000">
				<xsl:apply-templates/>
			</span>
		</span>
	</xsl:if>

	<span>
		<xsl:attribute name="style">
			color:<xsl:value-of select="$correct_color"/>;
			<xsl:value-of select="$padding"/>
			<xsl:value-of select="$font-weight"/>
			position:relative;
			top:1.5em;
			left:-1.5em;
		</xsl:attribute>
		<xsl:value-of select="@value"/>
	</span>

	<!-- コメント用テンプレートを呼び出す -->
	<xsl:call-template name="comment"/>
</xsl:template>


<!-- 提案 2005.03.17 -->
<xsl:template match="//better">
	<span title="提案">
	<xsl:if test="string-length(.)">
		<xsl:choose>
			<xsl:when test="@value">
				<span>
					<xsl:attribute name="style">
						<xsl:value-of select="$margin"/>
						<xsl:value-of select="$padding"/>
						border:<xsl:value-of select="$better_color"/> 1px solid;
						<xsl:value-of select="$font-weight"/>
					</xsl:attribute>
					<xsl:apply-templates/>
				</span>
			</xsl:when>
			<xsl:otherwise>
				<!-- 提案: 削除の場合に打消線 -->
				<span>
					<xsl:attribute name="style">
						color:<xsl:value-of select="$better_color"/>;
						margin:<xsl:value-of select="$margin"/>;
						padding:<xsl:value-of select="$padding"/>;
						border:<xsl:value-of select="$better_color"/> 1px solid;
						<xsl:value-of select="$font-weight"/>
						text-decoration:line-through;
					</xsl:attribute>
					<span style="color:#000000">
						<xsl:apply-templates/>
					</span>
				</span>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:if>
	<xsl:if test="@value">
		<span>
			<xsl:attribute name="style">
				color:<xsl:value-of select="$better_color"/>;
				<xsl:value-of select="$padding"/>
				<xsl:value-of select="$font-weight"/>
				position:relative;
				top:1.5em;left:-1.5em;
				font-size:small;
			</xsl:attribute>
			<xsl:value-of select="@value"/>
		</span>
	</xsl:if>

	<!-- コメント用テンプレートを呼び出す -->
	<xsl:call-template name="comment"/>

	</span>
</xsl:template>


<!-- 不明瞭 2005.03.17 -->
<xsl:template match="//unclear">
	<span title="不明瞭">
		<span>
			<xsl:attribute name="style">
				<xsl:value-of select="$margin"/>
				border-bottom:2px <xsl:value-of select="$comment_color"/> dotted;
				<xsl:value-of select="$padding"/>
				<xsl:value-of select="$font-weight"/>
			</xsl:attribute>
			<xsl:apply-templates/>
		</span>

		<!-- コメント用テンプレートを呼び出す -->
		<xsl:call-template name="comment">
			<xsl:with-param name="mark">?</xsl:with-param>
		</xsl:call-template>
	</span>
</xsl:template>


<!-- 改行: 段落を変える 2005.03.17 -->
<xsl:template match="//newparagraph">
	<span title="改行: 段落を変える">
		<xsl:attribute name="style">
			<xsl:value-of select="$margin"/>
			color:<xsl:value-of select="$correct_color"/>;
			font-size:4em;
			<xsl:value-of select="$font-weight"/>
			<xsl:value-of select="$font-family"/>
		</xsl:attribute>&#x21B5;</span>
</xsl:template>


<!-- 追込: 段落を変えない 2005.03.15 -->
<xsl:template match="//runon">
	<span title="改行: 段落を変える">
		<xsl:attribute name="style">
			<xsl:value-of select="$margin"/>
			color:<xsl:value-of select="$correct_color"/>;
			font-size:2.5em;
			<xsl:value-of select="$font-weight"/>
			<xsl:value-of select="$font-family"/>
		</xsl:attribute>&#x2621;</span>
</xsl:template>


<!-- 追込: 段落を変えない 2005.03.10 -->
<xsl:template match="//runon2">
	<img src="runon.png" alt="[追込]" title="追込: 段落を変えない"
	style="width:1.2em;height:1.2em;vertical-align:middle;margin:1em 0em;padding:0em;border:0em"/>
</xsl:template>


<!-- 学習者による改行の位置 2005.03.17 -->
<xsl:template match="//cp">
	<!-- font-family 指定無しだと IE6 で表示できない -->
	<span title="学習者による改行">
		<xsl:attribute name="style">
			<xsl:value-of select="$font-family"/>
		</xsl:attribute>&#x21B5;</span><br/>
</xsl:template>


<xsl:template match="//review">
</xsl:template>


<xsl:template match="//version">
</xsl:template>


<xsl:template match="//timestamp">
</xsl:template>


<xsl:template match="//writer">
</xsl:template>


<xsl:template match="//revisor">
</xsl:template>


<!-- コメント生成のため、関数的に呼び出すテンプレート -->
<xsl:template name="comment">
	<!-- 初期値を以下で指定 -->
	<!-- font-family 指定無しだと IE6 で表示できない -->
	<xsl:param name="mark">&#x270D;</xsl:param>
	<xsl:param name="id"><xsl:value-of select="generate-id()"/></xsl:param>

	<xsl:if test="string-length(@comment)">
		<span>
			<xsl:attribute name="style">
				color:<xsl:value-of select="$comment_color"/>;
				position:relative;
				top:-1.5em;
				left:-1.5em;
				font-size:small;
			</xsl:attribute>
			<a>
				<xsl:attribute name="style">
					color:<xsl:value-of select="$comment_color"/>;
					font-size:2em;
					<xsl:value-of select="$font-family"/>
				</xsl:attribute>
				<xsl:attribute name="href">javascript:display('<xsl:value-of select="$id"/>')</xsl:attribute>
				<span title="{@comment}"><xsl:value-of select="$mark"/></span>
			</a>

			<span style="background:#ddffdd;display:none">
				<xsl:attribute name="id"><xsl:value-of select="$id"/></xsl:attribute>
				<xsl:value-of select="@comment"/>
			</span>
		</span>
	</xsl:if>
</xsl:template>


<xsl:template match="text()">
	<xsl:value-of select="."/>
</xsl:template>


</xsl:stylesheet>
